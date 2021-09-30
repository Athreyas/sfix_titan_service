# Script Executor Service
This service has been developed using Python **Flask framework**. It is communicating with a local database store i.e, **sqlite3**. It allows users to perform multiple actions by reaching at various API endpoints. Below are list actions:
- List all the Scripts currently available in the DB
- When called by the Script name, it would list the contents of the script
- Upload a new script
- Run a existing script
- Get the status of the script execution

## Database service
Currently this service has been developed using sqlite3 database. It is named as **nebula.db** and is present with in the same project folder. Inorder to connect to this database run: `sqlite3 nebule.db`

This database currently has 2 tables
- titan_scripts
- scripts_status

## Dependencies
All the dependencies to run this service all provided with in the python virtual environment. One needs to activate the virtual environment by `source venv/bin/activate` below launching the applications.
This application has been developed using `Python 3.8.7` version.

## Steps to launch the application
- Activate the virtual environment. `source venv/bin/activate`
- Run the python command to launch the application. `python titan.py`
> This will launch the application on port 5002 and can be accessed at http://127.0.0.1:5002

## Improvements
- We would need to identify and authenticate the user before allowing him to execute.
- Before a user submits a script, it would need to check if the script already exists. If it does, we would need to increase the version counter and update the script column. Also have created_at and modified_at column in the scripts tables
- Before we execute a script, it would be better to check the if it is already inprogress and terminate/queue the reqeust.
