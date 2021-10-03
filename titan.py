# Script Executor service
# Service Name: Titan
# Database Name: nebula
# Author: Athreyas
# Version: 1.0

from flask import Flask, request, redirect, url_for, flash
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from werkzeug.utils import secure_filename
import os
import sqlite3
import subprocess

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'sh', 'py'}

app = Flask(__name__)
api = Api(app)
local_db = 'nebula.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        list_all_scripts = "select name from titan_scripts;"
        records = cursor.execute(list_all_scripts).fetchall()

        data = {
                'No.of Scripts available': len(records),
                'Scripts': records
            }

        return jsonify(data)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table  {}".format(error))

    finally:
        cursor.close()

# Below method will print the script with the given script_name
@app.route('/scripts/<string:script_name>/', methods=['GET'])
def fetch_script(script_name):
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        get_script = "SELECT command, is_file, file_name FROM titan_scripts WHERE name='{0}';".format(script_name)
        records = cursor.execute(get_script).fetchall()

        if records:
            record = list(records[0])
            if record[1]:
                script_path = os.path.join(app.config['UPLOAD_FOLDER'], record[2])
                file = open(script_path, 'r')
                content = file.read()
                file.close()

                output = {'Script File Name': record[2], 'Script Command': record[0], 'Script Content': content}
                return jsonify(output)

            else:
                return jsonify({'Name': script_name, 'Command': record[0]})

        else:
            output="Requesting script '{0}', doesn't exist in the DB".format(script_name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table  {}".format(error))

    finally:
        cursor.close()

# Below method will upload the script into DB
@app.route('/scripts/upload/', methods=['POST', 'GET'])
def upload_script():
    if request.method == 'POST':
        try:
            connection = sqlite3.connect(local_db)
            cursor = connection.cursor()

            if 'file' in request.files:
                attachment = request.files['file']

                if attachment and allowed_file(attachment.filename):
                    attachment_name = secure_filename(attachment.filename)
                    script_name = str(attachment_name.split('.')[0])
                    file_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment_name)
                    command="./"+file_upload_path
                    attachment.save(file_upload_path)

                    set_permission = 'chmod 755 '+file_upload_path
                    subprocess.run(set_permission, shell=True, check=True)

                    update_command = "insert into titan_scripts (name, command, is_file, file_name) values ('{0}', '{1}', True, '{2}');".format(script_name, command, attachment_name)
                    records = cursor.execute(update_command)
                    connection.commit()

                    output = {'Name': script_name, 'Script Command': command, 'Script File': attachment_name}
                    return jsonify(output)

            else:
                script_name = request.json.get('name')
                script_command = request.json.get('command')

                update_command = "insert into titan_scripts (name, command, is_file) values ('{0}', '{1}', False);".format(script_name, script_command)
                records = cursor.execute(update_command)
                connection.commit()

                output = {'Name': script_name, 'Script Command': script_command}
                return jsonify(output)

        except sqlite3.Error as error:
            return jsonify("Failed to connect to the database and insert into the table. {}".format(error))

        finally:
            cursor.close()

    else:
        return jsonify("Invaild method used. Only post method allowed.")


# Below method will run the input script
@app.route('/scripts/run/<string:script_name>/', methods=['GET'])
def run_script(script_name):
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        get_script_value = "SELECT uuid, command FROM titan_scripts WHERE name='{0}';".format(script_name)
        records = list(connection.execute(get_script_value).fetchall()[0])

        process = subprocess.run(records[1], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)


        if not process.returncode:
            update_script_output = "insert into titan_status (script_uuid, script_name, script_output, script_status ) values( {0}, '{1}', '{2}', '{3}');".format(records[0], script_name, process.stdout, 'Completed')
            cursor.execute(update_script_output)
            connection.commit()

            return jsonify({"Script Status": "Submitted"})

        else:
            output = "Requesting script '{}', didn't run successfully".format(script_name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table {}".format(error))

    finally:
        cursor.close()

# Below method will get the script execution status
@app.route('/scripts/status/<string:script_name>/', methods=['GET'])
def get_script_status(script_name):
    try:
        connection = sqlite3.connect(local_db)
        cursor = connection.cursor()

        get_script_value = "SELECT script_uuid, run_timestamp, script_status, script_output FROM titan_status WHERE script_name='{0}' ORDER BY run_timestamp DESC LIMIT 1;".format(script_name)
        records = connection.execute(get_script_value).fetchall()

        if records:
            record = list(records[0])
            return jsonify({'Script Name': script_name, 'Last Run Timestamp': record[1], 'Execution Status': record[2], 'Output': record[3]})

        else:
            output = "Requested script '{0}', has not been executed so far.".format(script_name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table {}".format(error))

    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True, port='5002')
