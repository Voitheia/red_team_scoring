# Red Team Scoring

Ansible python api state collection with a React frontend, FastAPI backend, and a SQLModel(SQLite) database to facilitate quantitative red team scoring in CDE. Queries boxes for status of indicators of compromise (IOCs) to determine a team's score.

## File structure/Table of contents

<table>
<tr><td><pre>
.
├── <a href="#ansible-1">ansible/</a>
│   ├── plugins/
│   │   └── callback/
│   │       └── <a href="#ansible-callback-plugin-ansiblepluginscallbackscoring_queuepy">scoring_queue.py</a>   # Callback plugin for managing checks
│   ├── ansible.cfg                # Points to ./plugins/callback
│   ├── <a href="#ansible-inventory-ansibleinventory">inventory/</a>                 # Blue team network configurations
│   └── playbooks/
│       ├── check/                 # IOC checking playbooks
│       └── deploy/                # IOC deployment playbooks
├── react/         
│   ├── public/   
│   │   └── image.png              # Any logos or images   
│   ├──src/    
│   │   ├── api/                   # API Calls to backend  
│   │   ├── css/                   # All CSS files are stored here  
│   │   ├── components/            # Reusable components
│   │   ├── pages/                 # Store pages as React Functions
│   │   ├── types/                 # If using typescript store all types here
│   │   └── App.js                 # Entry point for react
│   └──package.json   
├── app/                           # FastAPI application
├── <a href="#fastapi-functionality">fastapi/</a>                       # FastAPI application
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── ansible/                   # Ansible integration
│   │   ├── __init__.py
│   │   ├── <a href="#ansible-checks-appansiblecheckspy">checks.py</a>              # Check execution logic
│   │   └── deploy.py              # Deploy execution logic
│   ├── database/                  # Database integration
│   │   ├── __init__.py
│   │   └── <a href="#db-writer-appdatabasedb_writerpy">db_writer.py</a>           # Database writer
│   └── routes/                    # API endpoints
│       ├── __init__.py
│       ├── <a href="#admin-approutersadminpy">admin.py</a>               # Admin control panel
│       ├── <a href="#detailed-info-approutersdetailspy">details.py</a>             # Detailed IOC status
│       ├── <a href="#login-approutersloginpy">login.py</a>               # Authentication
│       └── <a href="#scoreboard-approutersscoreboardpy">scoreboard.py</a>          # Main scoring display
├── db/
│   └── <a href="#database-dbdatabasedb">database.db</a>                # SQLite database (dev only)
├── iocs/                          # Indicator of Compromise assets
│   ├── <a href="#defining-iocs-iocsdefinitions">definitions/</a>               # YAML IOC definitions
│   ├── <a href="#ioc-checking-scripts-iocscheck_scripts">check_scripts/</a>             # Scripts to verify IOC status
│   │   ├── firewall/
│   │   ├── linux/
│   │   └── windows/
│   └── <a href="#ioc-deploy-scripts-iocsdeploy_scripts">deploy_scripts/</a>            # Scripts to plant IOCs
│       ├── firewall/
│       ├── linux/
│       └── windows/
└── <a href="#payloads-payloads">payloads/</a>                      # Binary files
</pre></td></tr>
</table>

## Components Overview
```
  ┌──────────────────────────────────────────────────────────┐
  │                    Blue Team Networks                    │
  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐  │
  │  │   Windows    │   │    Linux     │   │   Firewall   │  │
  │  │    Hosts     │   │    Hosts     │   │    Hosts     │  │
  │  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘  │
  │         │                  │                  │          │
  │         └──────────────────┴──────────────────┘          │
  │                            │                             │
  │                    SSH/WinRM Connections                 │
  └────────────────────────────┼─────────────────────────────┘
                               │
                               ▼
            ┌─────────────────────────────────────────┐
            │                ANSIBLE                  │
            │  ┌────────────────────────────────┐     │
            │  │   Playbooks & Check Scripts    │     │
            │  └────────────────────────────────┘     │
            │  ┌────────────────────────────────┐     │
            │  │   Callback Plugin (scoring)    │     │
            │  └────────────────┬───────────────┘     │
            └─────────────────────────────────────────┘
                                │
                        Check Results (JSON)
                                │
                                ▼
            ┌─────────────────────────────────────────┐
            │              FastAPI Backend            │
            │  ┌────────────────────────────────┐     │
            │  │        DB Writer Process       │     │
            │  └────────────────┬───────────────┘     │
            │  ┌─────────────┐  │  ┌──────────────┐   │
            │  │   Routes    │  │  │   Ansible    │   │
            │  │  (API)      │  │  │  Integration │   │
            │  └──────┬──────┘  │  └──────────────┘   │
            └─────────┼─────────┼─────────────────────┘
                      │         │
                      │         ▼
                      │   ┌─────────────────────┐
                      │   │  SQLModel (SQLite)  │
                      │   │   Database (*.db)   │
                      │   └─────────────────────┘
                      │
                API Requests
                      │
                      ▼
            ┌─────────────────────────────────────────┐
            │            React Frontend               │
            │  ┌────────────────────────────────┐     │
            │  │  • Scoreboard                  │     │
            │  │  • Admin Panel                 │     │
            │  │  • Team Details                │     │
            │  │  • Login/Auth                  │     │
            │  └────────────────────────────────┘     │
            └─────────────────────────────────────────┘
```
### Ansible

Automates deployment and checking of IOCs. Uses SSH or WinRM, depending on the host OS, for remote command execution. 

### React (80/443)

Frontend for the scoreboards and admin functionality.

### FastAPI (8000)

Interconnection between other components. Serves data to React from an API and provides test/admin funcitonality. Has an Ansible callback plugin that captures check results and stores them in SQLModel.

### SQLModel(SQLite)

This data is based.

### IOCs

Defined in yml files, these are persistence mechanisms or misconfigurations that can be deployed or have their status checked with a corresponding script.

## Scoring info

- 10 IOCs per box
- even split between easy (1), medium (2) and hard (3)
  - (4, 3, 3)
- these give 10, 15, 20 points respectively.
- scores every 5 minutes

## Design principles

Needs to be as generic and config based as possible so its easy to reuse and modify in the future.

## IOCs `/iocs/`

### Defining IOCs `/iocs/definitions/`

An IOC is a single misconfiguration, persistence mechanism, etc. These are defined by YAML files in the naming format `<OS>_<IOC_NAME>.yml`, ex: `Windows_Service.yml`, `Linux_Cron.yml`. Each IOC YAML file contains the following information:
- Name of the IOC
- Description of the IOC
- Difficulty (Easy, Medium or Hard)
- OS (Windows, Linux, and/or Firewall)
- Script path that will check for the IOC (bash or powershell)
- Discovery: How are the blue teams intended to discover this IOC? (this is for white team)

#### Windows example

```yaml
name: malicious_service_win
description: Backdoor windows service listening on the network
difficulty: 2
os: windows
check_script: check_scripts/windows/Windows_Service_Check.ps1
deploy_script: deploy_scripts/windows/Windows_Service_Deploy.ps1
discovery: Check services.exe, sc.exe query, wmic, netstat, etc.
```

#### Linux example

```yaml
name: malicious_cron_lin
description: Backdoor cron job running every 5 minutes
difficulty: 1
os: linux
check_script: check_scripts/linux/Linux_Cron_Check.sh
deploy_script: deploy_scripts/linux/Linux_Cron_Deploy.sh
discovery: Check crontab -l and /etc/cron.d/
```

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

### IOC deploy scripts `/iocs/deploy_scripts`

Powershell or bash scripts that ansible will use to deploy the IOCs on the blue team networks. Scripts will follow the naming format `<OS>_<IOC_NAME>_Deploy.<EXT>`, ex: `Windows_Service_Deploy.ps1`, `Linux_Cron_Deploy.sh`.

## Payloads `/payloads/`

If an IOC needs a file to be deployed with it, such as `nc` for a simple listener, those files should be placed in the `/payloads/` directory. Use the `copy` ansible module for linux hosts and the `win_copy` module for windows hosts to pull payloads down to targets.

## Ansible

### Ansible inventory `/ansible/inventory`

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

Potentially have dynamic inventory generation like so:
```python
  # app/ansible/inventory_generator.py
  from ansible.inventory.manager import InventoryManager
  from ansible.parsing.dataloader import DataLoader

  class DynamicInventory:
      def __init__(self, team_config):
          self.base_network = team_config['base_network']  # e.g., "10.100"
          self.num_teams = team_config['num_teams']
          self.boxes = team_config['boxes']  # Template of boxes
          self.credentials = team_config['credentials']

      def generate_team_inventory(self, team_num):
          """Generate inventory for a specific team"""
          team_octet = self._calculate_team_octet(team_num)
          inventory = {
              f'team_{team_num}': {
                  'hosts': {},
                  'vars': {
                      'ansible_user': self.credentials['username'],
                      'ansible_password': self.credentials['password'],
                      'team_number': team_num
                  }
              }
          }

          for box in self.boxes:
              host_ip = f"{self.base_network}.{team_octet}.{box['ip_suffix']}"
              inventory[f'team_{team_num}']['hosts'][box['name']] = {
                  'ansible_host': host_ip,
                  'os_type': box['os'],
                  'box_name': box['name']
              }

          return inventory
```

```yaml
  # config/teams.yml
  base_network: "10.100"
  num_teams: 16
  team_ip_pattern: "{team_num}XX"  # Results in 101, 102, etc.
  credentials:
    username: admin
    password: ${ANSIBLE_PASSWORD}
  boxes:
    - name: dc01
      os: windows
      ip_suffix: 1
    - name: web01
      os: linux
      ip_suffix: 10
    - name: fw01
      os: firewall
      ip_suffix: 254
```

### Ansible checks `/app/ansible/checks.py`

Run every 5 minutes starting at competition start. Hardcoded start time configurable by admin. Admin also needs to "arm" checks. Need to be able to pause and restart for lunch, done manually.

Uses a multiprocessed ansible callback plugin to capture json output from check scripts and queue the output to a db writer process.

Need to look into:
- additional cleanup step to ensure temp files are removed even if execution is aborted
- locking the dirs that ansible puts temp files in somehow so that blue teams can't read them
- encrypting the scripts and hiding the encryption key somewhere, encryption key should be based on something related to the host, like hostname or ip

### Ansible callback plugin `/ansible/plugins/callback/scoring_queue.py`

Intended to be run as a subprocess so we can multiprocess the checks. Captures JSON output from the check scripts and queues it for the database writer process.

probably spawning 4 of these since ansible checks run synchronously. need to build a queue of playbooks to run for each check, and then have the worker processes grab new playbooks when its done with one. use ansible's python api.

#### Output parsing

```json
{
	"ip": "<IP_ADDRESS>",
	"os": "windows|linux|firewall",
	"ioc_name": "<IOC_NAME>",
	"status": -1|0|1, // -1=check failed, 0=remediated, 1=present
	"error": "<ERR_MSG>" // contains the error message if there is one
}
```

needs to become

- int IOCID (PK)
- int CheckID (FK -> Check_Instance: CheckID)
- str BoxIP
- str IOCName
- int Difficulty
- int Status
- str Error

IOCID gets assigned upon record creation. CheckID should be the most recent check for the blue team that matches the 3rd octet in the IP. We'll need a difficulty to IOCName mapping somewhere.

## Frontend

All pages besides login and scoreboard redirect to the login page if the user is not authenticated. Navigating to `/` will redirect the user to the scoreboard. Python files listed here contain the associated API functionality for the matching frontend page.

### FastAPI functionality

API functionality is defined below in this format:
```
Request Type (`GET`/`POST`)
- Request data 1
- Request data 2

Response
- Response data 1
- Response data 2
```

All response data will have a nullable `error` field unless otherwise mentioned.

### Navigation bar

Unauthenticated sessions have the login and scoreboard pages available.

Authenticated sessions have the logout, scoreboard, detailed info, and admin (if admin user) pages available.

login/logout will always be the rightmost link, separated from the rest by a `|`. the rest of the links are alphabetized and right justified.

Left side of the navigation bar will say `Red Team Score`, and clicking that will send the user to the scoreboard.

### Login `/app/routers/login.py`

Just simple username and password.

#### API `localhost:8000/login`

`POST`
- Username
- Password
  - will the site be http or https? do we care that we're throwing plaintext creds around? don't think it really matters for us

Response
- Session UUID
  - unsure how we should implement this, or if we even need to do it manually. FastAPI probably has something builtin to handle authentication and authorization

### Logout `/app/routers/login.py`

Just logs the user out and redirects the user to the login page.

#### API `localhost:8000/logout`

`POST`
- Session UUID

Response

### Scoreboard `/app/routers/scoreboard.py`

Graph/table showing all teams, their score, and how many points they earned last check. All users and unauthenticated users can access.

#### API `localhost:8000/scoreboard`

`GET`
- no args, this page should be the same for everyone, and isn't behind any authentication

Response
- Fields containing lists that comprise the graph. Time field will be populated with a timestamp for each check. Team fields will be populated with the total score of that team at that check.
```json
{
	"time": ["09:00", "09:05", "09:10"],
	"team0": [0, 15, 15],
	"team15": [0, 15, 30]
}
```

### Detailed info `/app/routers/details.py`

Blue teams are only able to see this page for their team. IOC names are obscured and follow the pattern `<OS>_<DIFFICULTY>_<NUM>`, ex: `WINDOWS_MEDIUM_2`, `LINUX_HARD_3`.

Any account that is not a blue team will be able to see all blue team's detailed info and see the actual name of the IOC like this: `<OS>_<IOC_NAME>_<DIFFICULTY>_<NUM>`, ex: `WINDOWS_SERVICE_MEDIUM_2`, `LINUX_CRON_HARD_3`.

#### API `localhost:8000/details`

`GET`
- Session UUID

Response
- Team's current total score
- Amount of points team earned from last check
- Fields containing lists that comprise the graph. Boxes have a list of `0/1`s corresponding to a check.
  - check list (static): `["EASY_1","EASY_2","EASY_3","EASY_4","MEDIUM_1","MEDIUM_2","MEDIUM_3","HARD_1","HARD_2","HARD_3"]`
```json
{
	"firewall": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	"linux_1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	"windows_1": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

### Admin `/app/routers/admin.py`

Only visible to `admin` user

Admin/Control panel
- run deploy scripts
- manually run checks
- set competition start time
- pause competition for lunch, able to start again
  - need to make sure we fully kill the process doing the automated checking here
- change user password
- clear check_instance and ioc_check_result tables, reset blue_teams score and lastcheckid

#### API `localhost:8000/admin/{}`

`localhost:8000/admin/deploy_iocs`: run deploy scripts 
- `GET`
  - Session UUID
- Response
  - script success/fail
  - nice to have: some way to view script output?

`localhost:8000/admin/run_checks`: manually run checks
- `GET`
  - Session UUID
- Response
  - returns when check is complete
  - nice to have: some way to view script output?

`localhost:8000/admin/start_time`: set competition start time
- `POST`
  - Session UUID
  - Time
- Response

`localhost:8000/admin/start_comp`: start competition
- `GET`
  - Session UUID
- Response
  - PID started

`localhost:8000/admin/stop_comp`: stop competition
- `GET`
  - Session UUID
- Response
  - PID killed

`localhost:8000/admin/change_pass`: change user password
- `POST`
  - Session UUID
  - Target user
  - New password
- Response

`localhost:8000/admin/reset_data`: clear check_instance and ioc_check_result tables, reset blue_teams score and lastcheckid
- `GET`
  - Session UUID
- Response
  - nullable error
  - nice to have: run a query that confirms tables and data have been reset


## Database `/db/database.db`

### DB Writer `/app/database/db_writer.py`

Consumes queue created by ansible callback plugin. Stores check results in the `IOC_Check_Result` table. Run as a subprocess to ensure that db writes don't get behind.

`Check_Instance` records should be created when that check starts.

### DB Tables

Use SQLModel to create and interact with these.

#### `Users`

Columns:
- int UserID (PK)
- str Username
- str Password (hashed)
- bool IsBlueTeam
- int BlueTeamNum (FK -> Blue_Teams: TeamNum)

Accounts:
- `blueteamXX` (00-16)
- `redteam`
- `whiteteam`
- `blackteam`
- `admin`

#### `Blue_Teams`

Columns:
- int TeamNum (PK)
- int null LastCheckID (FK -> Check_Instance: CheckID)

#### `Check_Instance`

Columns:
- int CheckID (PK)
- int BlueTeamNum (FK -> Blue_Teams: TeamNum)
- str Timestamp (iso 8601)
- int Score

#### `IOC_Check_Result`

Columns:
- int IOCID (PK)
- int CheckID (FK -> Check_Instance: CheckID)
- str BoxIP
- str IOCName
- int Difficulty
- int Status
- str Error

### DB Views

Used to dynamically calculate scores. Use direct sql connection to create and query these.

#### Base view for IOC points
```sql
CREATE VIEW IOC_Check_Result_With_Points AS
SELECT
  icr.*,
  CASE
      WHEN icr.Status = 0 THEN
          CASE icr.Difficulty
              WHEN 1 THEN 10
              WHEN 2 THEN 15
              WHEN 3 THEN 20
              ELSE 0
          END
      ELSE 0
  END AS Points
FROM IOC_Check_Result icr;
```

#### Calculate score gained from one check
```sql
CREATE VIEW Check_Instance_With_Score AS
SELECT
  ci.CheckID,
  ci.BlueTeamNum,
  ci.Timestamp,
  COALESCE(SUM(icrp.Points), 0) AS Score
FROM Check_Instance ci
LEFT JOIN IOC_Check_Result_With_Points icrp ON ci.CheckID = icrp.CheckID
GROUP BY ci.CheckID, ci.BlueTeamNum, ci.Timestamp;
```

#### Calculate scores for the scoreboard
```sql
CREATE VIEW Blue_Teams_Scoreboard AS
SELECT
  bt.TeamNum,
  bt.LastCheckID,
  COALESCE(
      (SELECT SUM(Score)
       FROM Check_Instance_With_Score
       WHERE BlueTeamNum = bt.TeamNum),
  0) AS TotalScore,
  COALESCE(last_check.Score, 0) AS LastCheckScore,
  last_check.Timestamp AS LastCheckTime
FROM Blue_Teams bt
LEFT JOIN Check_Instance_With_Score last_check
  ON bt.LastCheckID = last_check.CheckID;
```

#### Gather information for the details page
```sql
CREATE VIEW Team_Latest_IOC_Details AS
SELECT
  bt.TeamNum,
  icrp.BoxIP,
  icrp.IOCName,
  icrp.Difficulty,
  icrp.Status,
  icrp.Error,
  icrp.Points
FROM Blue_Teams bt
INNER JOIN IOC_Check_Result_With_Points icrp ON icrp.CheckID = bt.LastCheckID
ORDER BY bt.TeamNum, icrp.BoxIP, icrp.IOCName;
```

#### Score progression over time
```sql
CREATE VIEW Score_History AS
SELECT
  ci.BlueTeamNum AS TeamNum,
  ci.Timestamp,
  ci.Score AS CheckScore,
  (SELECT SUM(Score)
   FROM Check_Instance_With_Score ci2
   WHERE ci2.BlueTeamNum = ci.BlueTeamNum
     AND ci2.Timestamp <= ci.Timestamp) AS CumulativeScore
FROM Check_Instance_With_Score ci
ORDER BY ci.BlueTeamNum, ci.Timestamp;
```
