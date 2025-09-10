from pathlib import Path
import yaml

def initialize_competition(ioc_definitions, teams, playbook_cache):
    """Run once at competition start to generate all static components"""
    
    print("Initializing competition components...")
    
    # 1. Load IOC definitions (already passed in)
    print(f"Loaded {len(ioc_definitions)} IOC definitions")
    
    # 2. Generate static inventory
    inventory_path = generate_inventory(teams)
    
    # 3. Pre-generate all playbooks
    generate_all_playbooks(teams, ioc_definitions, playbook_cache)
    
    # 4. Validate all IOC scripts exist
    validate_ioc_scripts(ioc_definitions)
    
    print(f"Initialization complete. Generated {len(playbook_cache)} playbooks.")
    return inventory_path

def generate_inventory(teams) -> str:
    """Generate static inventory file with all hosts"""
    
    inventory = {
        'all': {
            'children': {
                'windows': {
                    'hosts': {},
                    'vars': {
                        'ansible_connection': 'psrp',
                        'ansible_port': 5985
                    }
                },
                'linux': {
                    'hosts': {},
                    'vars': {
                        'ansible_connection': 'ssh',
                        'ansible_port': 22,
                        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                    }
                },
                'firewall': {
                    'hosts': {},
                    'vars': {
                        'ansible_connection': 'ssh',
                        'ansible_port': 22,
                        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                    }
                }
            }
        }
    }
    
    # Add all team boxes
    for team in teams:
        for box in team.boxes:
            host_entry = {
                'ansible_host': box.ip,
                'ansible_user': 'admin',
                'ansible_password': 'password',
                'team_number': team.num,
                'box_name': box.name
            }
            
            # Add to appropriate OS group
            inventory['all']['children'][box.os]['hosts'][box.ip] = host_entry
    
    # Save inventory
    inventory_path = Path('/tmp/ioc_check_inventory.yml')
    with open(inventory_path, 'w') as f:
        yaml.dump(inventory, f)
    
    return str(inventory_path)

def generate_all_playbooks(teams, ioc_definitions, playbook_cache):
    """Pre-generate playbook for each unique box/IOC combination"""
    
    playbook_dir = Path('/tmp/ioc_playbooks')
    playbook_dir.mkdir(exist_ok=True)
    
    for team in teams:
        for box in team.boxes:
            iocs = get_iocs_for_os(box.os, ioc_definitions)
            
            for ioc in iocs:
                # Create unique playbook for this box/IOC combination
                playbook_key = f"{box.ip}_{ioc.name}"
                
                playbook = [{
                    'name': f'Check {ioc.name} on {box.ip}',
                    'hosts': box.ip,
                    'gather_facts': False,
                    'tasks': [{
                        'name': f'Execute {ioc.name} check',
                        'script': f'iocs/check_scripts/{box.os}/{ioc.check_script}',
                        'register': 'check_result',
                        'failed_when': False,
                        'changed_when': False,
                        'timeout': 30
                    }]
                }]
                
                # Save playbook
                playbook_path = playbook_dir / f'{playbook_key}.yml'
                with open(playbook_path, 'w') as f:
                    yaml.dump(playbook, f)
                
                # Cache the path
                playbook_cache[playbook_key] = str(playbook_path)

def get_iocs_for_os(os: str, ioc_definitions) -> list:
    """Get all IOCs for a specific OS"""
    
    return [ioc for ioc in ioc_definitions.values() if ioc.os.lower() == os.lower()]

def validate_ioc_scripts(ioc_definitions):
    """Validate that all IOC check and deploy scripts exist"""
    
    print("Validating IOC scripts...")
    missing_scripts = []
    
    for ioc_name, ioc in ioc_definitions.items():
        # Check if check script exists
        check_script_path = Path(f'iocs/check_scripts/{ioc.os}/{ioc.check_script}')
        if not check_script_path.exists():
            missing_scripts.append(f"Check script missing: {check_script_path}")
        
        # Check if deploy script exists (if specified)
        if hasattr(ioc, 'deploy_script') and ioc.deploy_script:
            deploy_script_path = Path(f'iocs/deploy_scripts/{ioc.os}/{ioc.deploy_script}')
            if not deploy_script_path.exists():
                missing_scripts.append(f"Deploy script missing: {deploy_script_path}")
    
    if missing_scripts:
        print("WARNING: Missing scripts:")
        for script in missing_scripts:
            print(f"  - {script}")
    else:
        print("All IOC scripts validated successfully")