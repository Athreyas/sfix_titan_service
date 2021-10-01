# Explaing Titan Service
## Assumptions made
- User would be running the solution solution from modern Linux environment such as MacOS.
- User will be running the scripts on the localhost.
- There is no user authentication and authorization.
- Have not developed the Web UI for this application.
- We could use the local database storage to store the script information.

## Approach to solve
I choose Flask framework to build this application and have used the sqlite database for the local storage.
Included API endpoints to use GET and POST method. A new script is submitted using POST method, it would make a insert call and update the table. We could also list all the scripts registered in the DB and run a script on local machine. Also obtain the script execution status.

## Limitations in Solution
- User wouldn't run multiple scripts simultaneously.
- User will not be able upload script file as attachment
- Script can't be ran on a remote machine.

## Improvements
- We would need to authenticate and authorize the user before allowing him to execute.
- Before a user submits a script, it would need to check if the script already exists. If it does, we would need to increment the version counter and update the script column. Also have created_at and modified_at column in the scripts_repo tables
- Before we execute a script, it would be better to check the if it is inprogress and terminate/queue the reqeust.

## Duration to complete
I was able to spend 1 hour over 4 days and complete the project.
