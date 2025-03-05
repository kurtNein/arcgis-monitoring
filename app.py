from arcpy.management import DowngradeAttachments
import datetime
from flask import Flask, render_template, jsonify, send_file
import json
import logging
import requests

from utils import AutoMod, EnterpriseMod

logging.info('Initialized app.py')

app = Flask(__name__)

def handle_timeout(url: str, timeout: int, message: str) -> str:
    status = message
    try:
        status = requests.get(url, timeout=timeout).status_code
    except TimeoutError as e:
        logging.error(e)
    finally:
        return str(status)

@app.route('/')
def index():
    # Home page endpoint. One-off procedures can be executed from UI on this page
    return render_template('index.html')

@app.route('/records.html')
def records():
    # Records page endpoint. Dashboard of common stats used when monitoring or troubleshooting.
    return render_template('records.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    # One-click call to class method which displays potentially unused feature services in the UI.
    am = AutoMod()
    unmapped_services_list = am.get_services_in_no_web_maps()
    data_dict = {}
    for service in unmapped_services_list:
        data_dict[service.title] = service.owner, service.id
    data = {'message': data_dict}
    return jsonify(data)

@app.route('/api/user', methods=['GET'])
def get_user():
    # One-click call to class method which displays potentially unused AGOL user licenses.
    am = AutoMod()
    inactive_users = am.get_inactive_users(return_type=list)
    data = {'message': inactive_users}
    return jsonify(data)

@app.route('/api/status', methods=['GET'])
def get_status():
    # Simple http request to any number of domains. Here to check on org domains which host GIS content.
    with open('creds.json') as f:
        # Store login credentials in another unversioned file.
        creds = json.load(f)
    data = {'message': {}}

    for domain in creds['domains']:

        logging.info(f"Sending https request to {creds['domains'][domain]}")

        domain_status = handle_timeout(creds['domains'][domain], 3, 'Timed out')
        data['message'][domain] = creds['domains'][domain], domain_status

        logging.info(f"Request to {creds['domains'][domain]} returned ")
    return jsonify(data)

@app.route('/api/backup_egdb', methods=['GET'])
def backup_egdb():
    em = EnterpriseMod()
    downloaded_items = em.download_items_locally()
    downloaded_items_formatted = {}
    for each in downloaded_items['egdb backup']:
        print(each, downloaded_items['egdb backup'][each])
        downloaded_items_formatted[f'{each}'] = str(downloaded_items['egdb backup'][each])
        print(downloaded_items_formatted)
    data = {'message': downloaded_items_formatted}
    return jsonify(data)

@app.route('/api/backup_agol', methods=['GET'])
def backup_agol():
    am = AutoMod()
    downloaded_items = am.download_items_locally()
    downloaded_items_formatted = {}
    for each in downloaded_items:
        print(each, downloaded_items[each])
        downloaded_items_formatted[f'{each}'] = str(downloaded_items[each])
        print(downloaded_items_formatted)
    data = {'message': downloaded_items_formatted}
    return jsonify(data)

@app.route('/api/last_stats', methods=['GET'])
def get_stats():
    with open('stats.json') as j:
        downloaded_items = json.load(j)
    downloaded_items_formatted = {}
    for each in downloaded_items['egdb backup']:
        print(each, downloaded_items['egdb backup'][each])
        downloaded_items_formatted[f'{each}'] = str(downloaded_items['egdb backup'][each])
        print(downloaded_items_formatted)
    data = {'message': downloaded_items_formatted}
    return jsonify(data)

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    # This is just for the default data for records.html.
    with open('stats.json') as j:
        downloaded_items = json.load(j)
        print(downloaded_items)
    total_items = len(downloaded_items['egdb backup'])
    failures = 0
    for item in downloaded_items['egdb backup']:
        # 'error' value is null in .json if it copied successfully, otherwise it should have the error text
        if downloaded_items['egdb backup'][item]['error']:
            failures += 1
    successes = total_items-failures
    data = {'message': {'Failures last backup': failures,
                        'Successes last backup': successes,
                        'Date of last backup': downloaded_items['last backup completed']}}
    return jsonify(data)

@app.route('/api/sde_users', methods=['GET'])
def list_sde_users():
    try:
        em = EnterpriseMod()
    except Exception as e:
        return jsonify({'message': e})
    users = em.list_users()
    data = {'message': users}
    return jsonify(data)

@app.route('/download', methods=['GET', 'POST'])
def download_file():
    print(True)
    try:
        path = r"./activity.log"
        return send_file(path, as_attachment=True)
    except Exception as e:
        logging.error(e)
        return jsonify({'message':{'Error': f'{e}'}})

if __name__ == '__main__':
    app.run(debug=True)
