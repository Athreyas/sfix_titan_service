# Script Executor Service
This service has been developed using Python **Flask framework**. It is communicating with a local database store i.e, **sqlite3**. It allows users to perform multiple actions by reaching at various API endpoints. Below are list actions:
- List all the Scripts currently available in the DB
- When called by the Script name, it would list the contents of the script
- Upload a new script
- Run a existing script
- Get the status of the script execution

## API endpoints
As mentioned above this service provides various API endpoints and each has a specific function. Below are the details:

|                        |Functionality                                 |Supported Methods |
|------------------------|----------------------------------------------|------------------|
|/                       |Home location                                 |GET               |
|/scripts/               |This will list all the scripts present in DB  |GET               |
|/scripts/<name>         |Prints the content of the scripts             |GET               |
|/scripts/post/          |Submit new script and store it in DB          |POST, GET         |
|/scripts/run/<name>     |Execute the script and update status          |GET               |
|/scripts/status/<name>  |Obtain the status of latest execution         |GET               |

## Database service
Currently this service has been developed using sqlite3 database. It is named as **nebula.db** and is present with in the same project folder. Inorder to connect to this database run: `sqlite3 nebule.db`

This database currently has 2 tables
- titan_repo
- titan_status

### Database Schema
- Table titan_repo

  `CREATE TABLE IF NOT EXISTS "titan_repo"(
uuid INTEGER PRIMARY KEY,
script_name TEXT NOT NULL,
script TEXT NOT NULL
);`
- Table titan_status

  `CREATE TABLE IF NOT EXISTS "titan_status"(
    uuid INTEGER,
    script_uuid INTEGER,
    run_timestamp datetime default current_timestamp,
    script_name TEXT NOT NULL,
    script_status TEXT,
    PRIMARY KEY (uuid),
    FOREIGN KEY (script_uuid)
      REFERENCES titan_scripts (uuid)
          ON DELETE CASCADE
          ON UPDATE NO ACTION
);`

### Database Sample Output

**titan_repo**
|uuid|script_name|script                                        |
|----|-----------|----------------------------------------------|
|1   |list       |ls -ltr                                       |
|2   |working_dir|pwd                                           |
|3   |username   |id -F                                         |
|4   |ip         |ifconfig en0 | grep 'inet ' | awk '{print $2}'|

**titan_status**
|uuid|script_uuid|run_timestamp      |script_name|script_status|
|----|-----------|-------------------|-----------|-------------|
|1   |   6       |2021-10-01 07:12:39|disk       |Completed    |
|2   |   1       |2021-10-01 07:13:10|list       |Completed    |
|3   |   2       |2021-10-01 07:13:18|working_dir|Completed    |
|4   |   3       |2021-10-01 07:13:27|username   |Completed    |
|5   |   4       |2021-10-01 07:13:49|ip         |Completed    |
|6   |   4       |2021-10-01 07:26:09|ip         |Completed    |

---

# Configuration
We need to have python ***virtualenv*** available inorder to create virtual environment and install dependencies. All the requried dependencies are provided as part of the ***requirements.txt***.
We will needs to create a virtualenv, activate the environment, install all the dependencies and then launch the application.
> This application has been developed using `Python 3.9.1` version.

## Steps to launch the application
- Download the tar file and unzip it. Navigate into `sfix_titan_service` directory.
- Create the virtual environment `python3 -m virtualenv venv`
- Activate the virtual environment `source venv/bin/activate`
- Now install all the dependencies `pip install -r requirements.txt`
- Launch the service `python titan.py`
> This will launch the application on port 5002 and can be accessed at http://127.0.0.1:5002

## Methods to access Titan service
The Flask application can be accessed from browser or from commandline using curl or wget module.
Assuming this `curl` will be used, below are couple of commands to be used:
- `curl http://127.0.0.1:5002/` : This will display the landing/home page.
- `curl http://127.0.0.1:5002/scripts/` : This will list all the scripts present in the DB currently.
- `curl http://127.0.0.1:5002/scripts/list/` : This will return ***list*** script information.
- `curl --header "Content-Type: application/json" --request POST --data '{ "script_name": "list", "script_value": "ls -ltr" }' http://localhost:5002/scripts/post/` : This will post new script and update the database.

    Input data is provided as json. Example: `{ "script_name": "disk", "script_value": "df -h" }`
- `curl http://127.0.0.1:5002/scripts/run/list/` : This will run the script `list` and save the process output to titan_status table.
- `curl http://127.0.0.1:5002/scripts/status/disk/` : This will return the script execution status

### Example post data
- `curl --header "Content-Type: application/json" --request POST --data '{ "script_name": "disk", "script_value": "df -h" }' http://localhost:5002/scripts/post/`
- `curl --header "Content-Type: application/json" --request POST --data '{ "script_name": "python_version", "script_value": "python --version" }' http://localhost:5002/scripts/post/`
- `curl --header "Content-Type: application/json" --request POST --data '{ "script_name": "count_lines", "script_value": "cat README.md | wc -l" }' http://localhost:5002/scripts/post/`
