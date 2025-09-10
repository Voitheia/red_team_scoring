import queue
import time
import threading
import ansible_runner

def worker(task_queue, retry_queue, shutdown_event, stats, stats_lock, 
          inventory_path, ioc_definitions, db_session):
    """Worker thread - consumes tasks from queue"""
    
    while not shutdown_event.is_set():
        try:
            # Get task with short timeout to check shutdown signal
            task = task_queue.get(timeout=0.5)
            
            # Update stats
            with stats_lock:
                stats['in_progress'] += 1
                stats['queue_size'] = task_queue.qsize()
            
            # Execute the check
            try:
                result = run_single_ioc_check(
                    task, inventory_path, ioc_definitions, db_session
                )
                
                with stats_lock:
                    if result['status'] == 0:
                        stats['completed'] += 1
                    else:
                        stats['failed'] += 1
                        # Add to retry queue if first attempt
                        if task.attempt == 1:
                            retry_queue.append(task)
                            
            except TimeoutError:
                with stats_lock:
                    stats['timeouts'] += 1
                    if task.attempt == 1:
                        retry_queue.append(task)
                        
            except Exception as e:
                print(f"Worker error processing {task.ioc_name} on {task.box_ip}: {e}")
                with stats_lock:
                    stats['failed'] += 1
                    if task.attempt == 1:
                        retry_queue.append(task)
            
            finally:
                # Update stats and mark done
                with stats_lock:
                    stats['in_progress'] -= 1
                task_queue.task_done()
                
        except queue.Empty:
            continue

def run_single_ioc_check(task, inventory_path, ioc_definitions, db_session):
    """Execute one IOC check using pre-generated playbook"""
    
    start_time = time.time()
    
    try:
        # Use cached playbook
        result = ansible_runner.run(
            inventory=inventory_path,
            playbook=task.playbook_path,
            quiet=True,
            timeout=30,
            cmdline='--ssh-common-args="-o ConnectTimeout=30 -o StrictHostKeyChecking=no"'
        )
        
        # Get IOC definition for parsing
        ioc = ioc_definitions.get(task.ioc_name)
        
        # Parse result using IOC-specific parser
        if result.stdout and ioc:
            parsed_output = parse_ioc_check_output(result.stdout, ioc)
            status = parsed_output.get('status', -1)
            output_data = parsed_output
        else:
            status = 0 if result.rc == 0 else -1
            output_data = {"status": status, "rc": result.rc}
        
        # Save to database with IOC metadata
        save_check_result(
            db_session,
            task=task,
            status=status,
            output_data=output_data,
            execution_time=time.time() - start_time
        )
        
        return {'status': status, 'task': task}
        
    except Exception as e:
        # Save failure to database
        save_check_result(
            db_session,
            task=task,
            status=-1,
            output_data={'error': str(e)},
            execution_time=time.time() - start_time
        )
        
        raise

def parse_ioc_check_output(stdout: str, ioc) -> dict:
    """Parse the JSON output from an IOC check script"""
    
    import json
    
    try:
        # Look for JSON in output (should be last line)
        lines = stdout.strip().split('\n')
        json_output = None
        
        for line in reversed(lines):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_output = json.loads(line)
                break
        
        if not json_output:
            return {
                "status": -1,
                "error": "No JSON output found in script response"
            }
        
        # Validate expected fields
        if json_output.get('status') not in [-1, 0, 1]:
            return {
                "status": -1,
                "error": f"Invalid status value: {json_output.get('status')}"
            }
        
        return json_output
        
    except json.JSONDecodeError as e:
        return {
            "status": -1,
            "error": f"Failed to parse JSON output: {e}"
        }
    except Exception as e:
        return {
            "status": -1,
            "error": f"Unexpected error parsing output: {e}"
        }

def save_check_result(db_session, task, status: int, output_data: dict, 
                      execution_time: float):
    """Save check result to database"""
    
    from fastapi_backend.database.models import IOCCheckResult
    
    # Create result record
    result = IOCCheckResult(
        check_instance_id=task.check_id,
        box_ip=task.box_ip,
        ioc_name=task.ioc_name,
        difficulty=task.difficulty if hasattr(task, 'difficulty') else 0,
        status=status,
        error=output_data.get('error')
    )
    
    # Save to database
    db_session.add(result)
    db_session.commit()
    
    return result