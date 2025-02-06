import logging
from flask import Flask, render_template, jsonify, request
from sqlalchemy.sql.type_api import NULLTYPE

from utils import AutoMod, EnterpriseMod
from smtplib import SMTP
import datetime
import json
import requests

logging.info('Initialized app.py')

app = Flask(__name__)

am = AutoMod()

em = EnterpriseMod()

def send_email():
    DEBUG_LEVEL = 0

    smtp = SMTP()
    smtp.set_debuglevel(DEBUG_LEVEL)
    smtp.connect('YOUR.MAIL.SERVER', 26)
    smtp.login('USERNAME@DOMAIN', 'PASSWORD')

    from_addr = "John Doe <john@doe.net>"
    to_addr = "foo@bar.com"

    subj = "hello"
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    message_text = "Hello\nThis is a mail from your server\n\nBye\n"

    msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (from_addr, to_addr, subj, date, message_text)

    smtp.sendmail(from_addr, to_addr, msg)
    smtp.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/records.html')
def records():
    return render_template('records.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    # Example of sending some data from Python to the frontend

    unmapped_services_list = am.get_services_in_no_web_maps()
    data_dict = {}
    for service in unmapped_services_list:
        data_dict[service.title] = service.owner
    data = {'message': data_dict}
    return jsonify(data)

@app.route('/api/user', methods=['GET'])
def get_user():
    inactive_users = am.get_inactive_users(return_type=list)
    data = {'message': inactive_users}
    return jsonify(data)

@app.route('/api/status', methods=['GET'])
def get_status():
    # Example data for "Status"
    logging.info(f'Sending http request to "maps.mercercounty.org/portal", "pip.mercercounty.org"')
    portal_status = requests.get('https://maps.mercercounty.org/portal').status_code
    pip_status = requests.get('http://pip.mercercounty.org/signin').status_code
    data = {'message':
        {
        'maps.mercercounty.org/portal': f"Response: {str(portal_status)}",
        'pip.mercercounty.org/signin': f"Response: {str(pip_status)}"
        }
    }
    return jsonify(data)

@app.route('/api/backup', methods=['GET'])
def get_backup():
    downloaded_items = em.download_items_locally()
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
                        'Last EGDB backup': downloaded_items['last backup completed']}}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
