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
        cs = connection.cursor()

        list_all_scripts = "select script_name from titan_scripts;"
        records = cs.execute(list_all_scripts).fetchall()

        data = {
                'No.of Scripts available': len(records),
                'Scripts': records
            }

        return jsonify(data)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        connection.close()

# Below method will print the script with the given script_name
@app.route('/scripts/<string:name>/', methods=['GET'])
def fetch_script(name):
    try:
        connection = sqlite3.connect(local_db)
        cs = connection.cursor()

        get_script_value = "SELECT script FROM titan_scripts WHERE script_name='{0}';".format(name)
        record = list(cs.execute(get_script_value).fetchall()[0])

        if record:
            return jsonify({'Name': name, 'Script': record[0]})
        else:
            output="Requesting script {}, doesn't exist in the DB".format(name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        connection.close()

# Below method will upload the script into DB
@app.route('/scripts/push/', methods=['GET', 'POST'])
def upload_script():
    script = request.args.get('script')

    try:
        connection = sqlite3.connect(local_db)
        cs = connection.cursor()

        if request.method == 'POST':
            script_name = request.form.get('script_name')
            script = request.form.get('script')

            update_command = "insert into titan_scripts values(null, '{0}', '{1}');".format(script_name, script)
            record = connection.execute(update_command)

            output = '''
                      <h1>Script name is: {}</h1>
                      <h1>Input Script is: {}</h1>'''.format(script_name, script)
            return output

        else:
            output = '''
                      <form method="POST">
                          <div><label>Script Name: <input type="text" name="script_name"></label></div>
                          <div><label>Scripts: <input type="text" name="script"></label></div>
                          <input type="submit" value="Submit">
                      </form>'''
            return output

    except sqlite3.Error as error:
        return jsonify("Failed to insert records into the table")

    finally:
        connection.close()

# Below method will run the input script
@app.route('/scripts/run/<string:name>/', methods=['GET'])
def run_script(name):
    try:
        connection = sqlite3.connect(local_db)
        cs = connection.cursor()

        get_script_value = "SELECT uuid, script FROM titan_scripts WHERE script_name='{0}';".format(name)
        record = list(cs.execute(get_script_value).fetchall()[0])


        if record:
            process = subprocess.run(record[1], shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = process.stdout

            update_script_output = "insert into titan_scripts_status values(null, {0}, '{1}', ,'{2}');".format(record[0], name, output)
            update_output = cs.execute(update_script_output).fetchall()

            return jsonify(output, update_output)

        else:
            output="Requesting script '{}', doesn't exist in the DB".format(name)
            return jsonify(output)

    except sqlite3.Error as error:
        return jsonify("Failed to read data from table")

    finally:
        connection.close()

# Below method will get the script execution status
@app.route('/scripts/status/<string:name>/', methods=['GET'])
def get_script_status(name):
    return "Status of the script '{}' execution is as follows".format(name)


if __name__ == '__main__':
    app.run(debug=True, port='5002')
