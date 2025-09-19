from dataclasses import dataclass
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

import yaml

@dataclass
class IOCDefinition:
    """Represents a single IOC definition"""
    name: str
    description: str
    difficulty: int  # 1=Easy, 2=Medium, 3=Hard
    os: str  # windows, linux, or firewall
    check_script: str  # Relative path from iocs/check_scripts/{os}/
    deploy_script: Optional[str]  # Relative path from iocs/deploy_scripts/{os}/
    discovery: str  # How blue teams should discover this IOC
    points: int = 0  # Calculated from difficulty

    def __post_init__(self):
        """Calculate points based on difficulty"""
        difficulty_to_points = {1: 10, 2: 15, 3: 20}
        self.points = difficulty_to_points.get(self.difficulty, 0)

class IOCDefinitionLoader:
    """Loads and manages IOC definitions from YAML files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ioc_definitions: Dict[str, IOCDefinition] = {}
        self.os_ioc_mapping: Dict[str, List[IOCDefinition]] = {
            'windows': [],
            'linux': [],
            'firewall': []
        }

    def load_ioc_definitions(self):
        """Load all IOC definitions from YAML files"""

        definitions_path = Path('iocs/definitions')
        ioc_files = list(definitions_path.glob('*.yml')) + list(definitions_path.glob('*.yaml'))

        self.logger.info(f"Loading {len(ioc_files)} IOC definitions...")

        for ioc_file in ioc_files:
            try:
                with open(ioc_file, 'r') as f:
                    data = yaml.safe_load(f)

                # Validate required fields
                required_fields = ['name', 'description', 'difficulty', 'os', 'check_script']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.logger.warning(f"Skipping {ioc_file}: missing fields {missing_fields}")
                    continue

                # Create IOC definition
                ioc = IOCDefinition(
                    name=data['name'],
                    description=data['description'],
                    difficulty=data['difficulty'],
                    os=data['os'].lower(),
                    check_script=data['check_script'],
                    deploy_script=data.get('deploy_script'),
                    discovery=data.get('discovery', 'Not specified')
                )

                # Store in both general dict and OS-specific lists
                self.ioc_definitions[ioc.name] = ioc

                if ioc.os in self.os_ioc_mapping:
                    self.os_ioc_mapping[ioc.os].append(ioc)
                else:
                    self.logger.warning(f"Unknown OS '{ioc.os}' in {ioc_file}")

            except Exception as e:
                self.logger.error(f"Error loading {ioc_file}: {e}")

        # Validate IOC distribution
        self.validate_ioc_distribution()

        self.logger.info(f"Loaded {len(self.ioc_definitions)} IOC definitions:")
        for os, iocs in self.os_ioc_mapping.items():
            self.logger.info(f"  - {os}: {len(iocs)} IOCs")

    def validate_ioc_distribution(self):
        """Ensure proper distribution of IOCs per OS (4 easy, 3 medium, 3 hard)"""

        expected_distribution = {1: 4, 2: 3, 3: 3}  # difficulty: count

        for os, iocs in self.os_ioc_mapping.items():
            if not iocs:
                continue

            # Count by difficulty
            difficulty_counts = {1: 0, 2: 0, 3: 0}
            for ioc in iocs:
                difficulty_counts[ioc.difficulty] += 1

            # Check distribution
            for difficulty, expected_count in expected_distribution.items():
                actual_count = difficulty_counts[difficulty]
                if actual_count != expected_count:
                    self.logger.warning(f"{os} has {actual_count} difficulty-{difficulty} IOCs, expected {expected_count}")

    def get_iocs_for_os(self, os: str) -> List[IOCDefinition]:
        """Get all IOCs for a specific OS"""

        return self.os_ioc_mapping.get(os.lower(), [])

    def validate_ioc_scripts(self):
        """Validate that all IOC check and deploy scripts exist"""

        self.logger.info("Validating IOC scripts...")
        missing_scripts = []

        for ioc_name, ioc in self.ioc_definitions.items():
            # Check if check script exists (prefix with iocs/)
            check_script_path = Path("iocs") / ioc.check_script
            if not check_script_path.exists():
                missing_scripts.append(f"Check script missing: {check_script_path}")

            # Check if deploy script exists (if specified)
            if ioc.deploy_script:
                deploy_script_path = Path("iocs") / ioc.deploy_script
                if not deploy_script_path.exists():
                    missing_scripts.append(f"Deploy script missing: {deploy_script_path}")

        if missing_scripts:
            self.logger.error(f"Missing {len(missing_scripts)} required scripts:")
            for script in missing_scripts:
                self.logger.error(f"  - {script}")
            raise FileNotFoundError(f"Missing {len(missing_scripts)} required scripts")

        self.logger.info(f"All scripts validated successfully")

    def parse_ioc_check_output(self, stdout: str, ioc: IOCDefinition) -> Dict:
        """Parse the JSON output from an IOC check script"""

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