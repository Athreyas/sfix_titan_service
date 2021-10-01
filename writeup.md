# Explaing Titan Service
## Assumptions made


## Approach to solve


## Limitations in Solution


## Improvements
- We would need to identify and authenticate the user before allowing him to execute.
- Before a user submits a script, it would need to check if the script already exists. If it does, we would need to increase the version counter and update the script column. Also have created_at and modified_at column in the scripts tables
- Before we execute a script, it would be better to check the if it is already inprogress and terminate/queue the reqeust.

## Duration to complete
