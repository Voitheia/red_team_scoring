from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import yaml
import logging
import json

@dataclass
class Box:
    """Represents a single box/host in the competition"""
    ip: str
    name: str
    os: str  # 'windows', 'linux', or 'firewall'
    team_num: int
    username: str = "admin"
    password: str = "password"
    port: Optional[int] = None
    connection: Optional[str] = None  # 'winrm', 'psrp', or None for default

    def __post_init__(self):
        if self.port is None:
            self.port = 5985 if self.os == 'windows' else 22
        if self.connection is None and self.os == 'windows':
            self.connection = 'winrm'  # Default to winrm for Windows

@dataclass
class Team:
    """Represents a blue team"""
    team_num: int
    name: str
    boxes: List[Box] = field(default_factory=list)

class InventoryManager:
    """
    Manages team and box inventory for the competition.
    Generates Ansible inventory files and tracks host information.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.teams: Dict[int, Team] = {}
        self.all_boxes: List[Box] = []
        self.inventory_path: Optional[Path] = None
        self.ansible_dir = Path("./ansible")
        self.ansible_dir.mkdir(exist_ok=True)

    def load_from_config(self, config_path: Optional[Path] = None) -> None:
        """Load inventory from configuration file"""
        if config_path is None:
            # Try test inventory first, then regular inventory, then defaults
            test_config = Path("./config/test_inventory.yml")
            regular_config = Path("./config/inventory.yml")

            if test_config.exists():
                config_path = test_config
                self.logger.info(f"Using test inventory: {config_path}")
            elif regular_config.exists():
                config_path = regular_config
                self.logger.info(f"Using regular inventory: {config_path}")
            else:
                self.logger.warning(f"No inventory config found, using defaults")
                self._create_default_inventory()
                return

        if config_path.exists():
            self.logger.info(f"Loading inventory from {config_path}")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self._parse_config(config)
        else:
            self.logger.warning(f"Inventory config not found at {config_path}, using defaults")
            self._create_default_inventory()

    def _parse_config(self, config: Dict) -> None:
        """Parse inventory configuration"""
        for team_data in config.get('teams', []):
            team = Team(
                team_num=team_data['team_num'],
                name=team_data.get('name', f"Team {team_data['team_num']}")
            )

            for box_data in team_data.get('boxes', []):
                box = Box(
                    ip=box_data['ip'],
                    name=box_data['name'],
                    os=box_data['os'].lower(),
                    team_num=team.team_num,
                    username=box_data.get('username', 'admin'),
                    password=box_data.get('password', 'password'),
                    port=box_data.get('port'),
                    connection=box_data.get('connection')
                )
                team.boxes.append(box)
                self.all_boxes.append(box)

            self.teams[team.team_num] = team

        self.logger.info(f"Loaded {len(self.teams)} teams with {len(self.all_boxes)} total boxes")

    def _create_default_inventory(self) -> None:
        """Create a minimal test inventory for MVP"""
        self.logger.info("Creating default test inventory")

        # Create 2 test teams with 2 boxes each for MVP testing
        for team_num in [1, 2]:
            team = Team(team_num=team_num, name=f"Team {team_num}")

            # Linux box
            linux_box = Box(
                ip=f"10.0.{team_num}.10",
                name=f"team{team_num}-linux",
                os="linux",
                team_num=team_num,
                username="admin",
                password="password"
            )
            team.boxes.append(linux_box)
            self.all_boxes.append(linux_box)

            # Windows box
            windows_box = Box(
                ip=f"10.0.{team_num}.20",
                name=f"team{team_num}-windows",
                os="windows",
                team_num=team_num,
                username="admin",
                password="password"
            )
            team.boxes.append(windows_box)
            self.all_boxes.append(windows_box)

            self.teams[team_num] = team

        self.logger.info(f"Created default inventory: {len(self.teams)} teams, {len(self.all_boxes)} boxes")

    def generate_ansible_inventory(self) -> Path:
        """Generate Ansible inventory file"""
        inventory = {
            'all': {
                'children': {
                    'windows': {
                        'hosts': {},
                        'vars': {
                            'ansible_connection': 'winrm',
                            'ansible_winrm_transport': 'basic',
                            'ansible_winrm_scheme': 'http',
                            'ansible_port': 5985,
                            'ansible_winrm_server_cert_validation': 'ignore'
                        }
                    },
                    'linux': {
                        'hosts': {},
                        'vars': {
                            'ansible_connection': 'ssh',
                            'ansible_port': 22,
                            'ansible_ssh_common_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
                        }
                    },
                    'firewall': {
                        'hosts': {},
                        'vars': {
                            'ansible_connection': 'ssh',
                            'ansible_port': 22,
                            'ansible_ssh_common_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
                        }
                    }
                }
            }
        }

        # Add all boxes to appropriate OS groups
        for box in self.all_boxes:
            host_entry = {
                'ansible_host': box.ip,
                'ansible_user': box.username,
                'ansible_password': box.password,
                'team_number': box.team_num,
                'box_name': box.name
            }

            # Handle PSRP connection for Windows boxes
            if box.os == 'windows' and box.connection == 'psrp':
                host_entry['ansible_connection'] = 'psrp'
                host_entry['ansible_port'] = box.port or 5986
                host_entry['ansible_psrp_cert_validation'] = 'ignore'
                host_entry['ansible_psrp_auth'] = 'basic'
                host_entry['ansible_psrp_protocol'] = 'https'
            # Add port override if non-standard
            elif box.os == 'windows' and box.port != 5985:
                host_entry['ansible_port'] = box.port
            elif box.os in ['linux', 'firewall'] and box.port != 22:
                host_entry['ansible_port'] = box.port

            # Use IP as host identifier in inventory
            inventory['all']['children'][box.os]['hosts'][box.ip] = host_entry

        # Save inventory file
        self.inventory_path = self.ansible_dir / "inventory.yml"
        with open(self.inventory_path, 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False)

        self.logger.info(f"Generated Ansible inventory at {self.inventory_path}")
        return self.inventory_path

    def get_boxes_by_os(self, os: str) -> List[Box]:
        """Get all boxes with specific OS"""
        return [box for box in self.all_boxes if box.os.lower() == os.lower()]

    def get_team_boxes(self, team_num: int) -> List[Box]:
        """Get all boxes for a specific team"""
        team = self.teams.get(team_num)
        return team.boxes if team else []

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get summary of inventory for status API"""
        os_counts = {}
        for box in self.all_boxes:
            os_counts[box.os] = os_counts.get(box.os, 0) + 1

        return {
            "num_teams": len(self.teams),
            "num_boxes": len(self.all_boxes),
            "os_distribution": os_counts,
            "teams": [
                {
                    "team_num": team.team_num,
                    "name": team.name,
                    "num_boxes": len(team.boxes)
                }
                for team in self.teams.values()
            ]
        }

    def save_config(self, path: Optional[Path] = None) -> None:
        """Save current inventory to config file"""
        if path is None:
            config_dir = Path("./config")
            config_dir.mkdir(exist_ok=True)
            path = config_dir / "inventory.yml"

        config = {
            'teams': [
                {
                    'team_num': team.team_num,
                    'name': team.name,
                    'boxes': [
                        {
                            'ip': box.ip,
                            'name': box.name,
                            'os': box.os,
                            'username': box.username,
                            'password': box.password,
                            'port': box.port
                        }
                        for box in team.boxes
                    ]
                }
                for team in self.teams.values()
            ]
        }

        with open(path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        self.logger.info(f"Saved inventory config to {path}")