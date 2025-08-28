# Red Team Scoring

Ansible python api state collection with a FastAPI frontend and SQLModel backend to facilitate quantitative red team scoring in CDE. Queries boxes for status of IOCs to determine a team's score.

## File structure
```
.
├── ansible/
│   ├── inventory/               # Blue team network configurations
│   └── playbooks/
│       ├── check/               # IOC checking playbooks
│       └── deploy/              # IOC deployment playbooks
├── app/                         # FastAPI application
│   ├── __init__.py
│   ├── main.py                  # Application entry point
│   ├── ansible/                 # Ansible integration
│   │   ├── __init__.py
│   │   └── checks.py            # Check execution logic
│   └── routers/                 # API endpoints
│       ├── __init__.py
│       ├── details.py           # Detailed IOC status
│       ├── login.py             # Authentication
│       └── scoreboard.py        # Main scoring display
├── db/
│   └── database.db              # SQLite database (dev only)
└── iocs/                        # Indicator of Compromise assets
    ├── definitions/             # YAML IOC definitions
    ├── check_scripts/           # Scripts to verify IOC status
    │   ├── linux/
    │   └── windows/
    └── deploy_scripts/          # Scripts to plant IOCs
        ├── linux/
        └── windows/
```

## Scoring info

- 10 IOCs per box
- even split between easy, medium and hard (4, 3, 3)
- these give 10, 15, 20 points respectively.

## Design principles

Needs to be as generic and config based as possible so its easy to reuse and modify in the future.

## IOCs `/iocs/`

### Defining IOCs `/iocs/definitions/`

TODO: need examples for windows and linux

An IOC is a single misconfiguration, persistence mechanism, etc. These are defined by YAML files in the naming format `<OS>_<IOC_NAME>.yml`, ex: `Windows_Service.yml`, `Linux_Cron.yml`. Each IOC YAML file contains the following information:
- Name of the IOC
- Description of the IOC
- Difficulty (Easy, Medium or Hard)
- OS (Windows, Linux, and/or Firewall)
- Script path that will check for the IOC (bash or powershell)
- Discovery: How are the blue teams intended to discover this IOC? (this is for white team)

### IOC checking scripts `/iocs/check_scripts`

Powershell or bash scripts that ansible will use to check the status of an IOC. Scripts will follow the naming format `<OS>_<IOC_NAME>_Check.<EXT>`, ex: `Windows_Service_Check.ps1`, `Linux_Cron_Check.sh`.

#### IOC checking scripts return format

JSON output:
```json
{
	"ip": "<IP_ADDRESS>",
	"os": "windows|linux|firewall",
	"ioc_name": "<IOC_NAME>",
	"status": -1|0|1, // -1=check failed, 0=remediated, 1=present
	"error": "<ERR_MSG>" // contains the error message if there is one
}
```

TODO: make one big json per IP?

### IOC deploy scripts `/iocs/deploy_scripts`

Powershell or bash scripts that ansible will use to deploy the IOCs on the blue team networks. Scripts will follow the naming format `<OS>_<IOC_NAME>_Deploy.<EXT>`, ex: `Windows_Service_Deploy.ps1`, `Linux_Cron_Deploy.sh`.

## Blue team network config files `/ansible/inventory`

YAML file(s) that define the blue team networks:
- Number of teams
- IP /16 (ex: 10.100.0.0/16)
- Blue teams IP 3rd octet format (Team 1 example: 1XX, XX, etc. - 10.100.101.0/24, 10.100.1.0/24)
- Username to use
- Password to use
- List of boxes
	- name of box
	- OS (Windows, Linux, or Firewall)
	- IP 4th octet (10.100.101.XXX - 10.100.101.1/10.100.101.101)

TODO: need example

## Ansible checks `/app/ansible/checks.py`

Run every 5 minutes starting at competition start. Hardcoded start time.

Create an ansible callback plugin that will use a python queue to queue results from the ansible checks. messages in the queue are processed by a single separate process db writer. spawn multiple (probably 4) worker processes to run the ansible checks since they run synchronously. build a queue of playbooks to run for each check, and then have the worker processes grab new playbooks when its done with one. make sure to use ansible's python api instead of the ansible-playbook cli.

## Frontend `/app/routers/`

All pages besides login and scoreboard redirect to the login page if the user is not authenticated.

### Login `/app/routers/login.py`

Just simple username and password.

### Scoreboard `/app/routers/scoreboard.py`

Graph/table showing all teams, their score, and how many points they earned last check. All users and unauthenticated users can access.

### Detailed info `/app/routers/details.py`

Blue teams are only able to see this page for their team. IOC names are obscured and follow the pattern `<OS>_<DIFFICULTY>_<NUM>`, ex: `WINDOWS_MEDIUM_2`, `LINUX_HARD_3`.

Any account that is not a blue team will be able to see all blue team's detailed info and see the actual name of the IOC like this: `<OS>_<IOC_NAME>_<DIFFICULTY>_<NUM>`, ex: `WINDOWS_SERVICE_MEDIUM_2`, `LINUX_CRON_HARD_3`.

## Backend `/db/database.db`

### DB Tables

#### `Users`

Username (PK), Password (hashed), IsBlueTeam, BlueTeamNum (FK)

Accounts:
- `blueteamXX` (00-16)
- `redteam`
- `whiteteam`
- `blackteam`
- `admin`

BlueTeamNum -> Blue_Teams: TeamNum

#### `Blue_Teams`

TeamNum (PK), TotalScore, LastCheckJSONID (FK)

TODO: we should be able to calculate the total score with a sql add/query thing
- some sorta `SELECT SUM(ScoreAdded) AS TotalScore FROM Check_Instance WHERE BlueTeamNum = TeamNum`

LastCheckJSONID -> Check_Instance: ID

#### `Check_Instance`

ID (PK), BlueTeamNum (FK), ScoreAdded, CheckJSON