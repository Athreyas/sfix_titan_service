from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import sqlite3
import subprocess

app = Flask(__name__)
api = Api(app)
local_db = 'nebula.db'

@app.route('/', methods=['GET'])
def home():
    output = '''
              <center><h1>Script Executor Service</h1>
              <h3>This service is built using Flask</h3>
              <p>It allows users to list, submit, and execute bash scripts</p></center>'''
    return output

# Below method will list all the scripts currently saved in DB
@app.route('/scripts/', methods=['GET'])
def list_script_names():
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        list_all_scripts = "select script_name from titan_repo;"
        records = cursor.execute(list_all_scripts).fetchall()

        data = {
                'No.of Scripts available': len(records),
                'Scripts': records
            }

        return jsonify(data)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        cursor.close()

# Below method will print the script with the given script_name
@app.route('/scripts/<string:name>/', methods=['GET'])
def fetch_script(name):
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        get_script_value = "SELECT script FROM titan_repo WHERE script_name='{0}';".format(name)
        records = cursor.execute(get_script_value).fetchall()

        if records:
            record = list(records[0])
            return jsonify({'Name': name, 'Script': record[0]})
        else:
            output="Requesting script '{0}'', doesn't exist in the DB".format(name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        cursor.close()

# Below method will upload the script into DB
@app.route('/scripts/post/', methods=['POST', 'GET'])
def upload_script():
    script = request.args.get('script')

    if request.method == 'POST':
        try:
            connection = sqlite3.connect(local_db)
            cursor = connection.cursor()

            script_name = request.json.get('script_name')
            script_value = request.json.get('script_value')

            update_command = "insert into titan_repo (script_name, script) values ('{0}', '{1}');".format(script_name, script_value)
            records = cursor.execute(update_command)
            connection.commit()

            output = {'Name': script_name, 'Script Value': script_value}
            return jsonify(output)

        except sqlite3.Error as error:
            return jsonify("Failed to connect to the database and insert into the table")

        finally:
            cursor.close()

    else:
        return jsonify("Invaild method used. Only post method allowed.")


# Below method will run the input script
@app.route('/scripts/run/<string:name>/', methods=['GET'])
def run_script(name):
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        script_name = name
        get_script_value = "SELECT uuid, script FROM titan_repo WHERE script_name='{0}';".format(script_name)
        records = list(connection.execute(get_script_value).fetchall()[0])

        process = subprocess.run(records[1], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)

        if not process.returncode:
            update_script_output = "insert into titan_status (script_uuid, name, script_status ) values( {0}, '{1}', '{2}');".format(records[0], script_name, 'Completed')
            cursor.execute(update_script_output)
            connection.commit()

            return jsonify({"Script Status": "Submitted", "Script Output": process.stdout})

        else:
            output = "Requesting script '{}', didn't run successfully".format(name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        cursor.close()

# Below method will get the script execution status
@app.route('/scripts/status/<string:name>/', methods=['GET'])
def get_script_status(name):
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        script_name = name
        get_script_value = "SELECT script_uuid, run_timestamp, script_status FROM titan_status WHERE script_name='{0}' ORDER BY run_timestamp DESC LIMIT 1;".format(script_name)
        records = connection.execute(get_script_value).fetchall()

        if records:
            record = list(records[0])
            output = "Latest status of the script '{0}' is: {1}".format(script_name, record[2])
            return jsonify(output)

        else:
            output = "Requested script '{0}', has not been executed so far.".format(script_name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True, port='5002')
    #app.run(port='5002')
