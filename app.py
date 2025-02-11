import logging

from arcpy.management import DowngradeAttachments
from flask import Flask, render_template, jsonify, request
from utils import AutoMod, EnterpriseMod
from smtplib import SMTP
import datetime
import json
import requests

logging.info('Initialized app.py')

app = Flask(__name__)

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
    return render_template('index.html')

@app.route('/records.html')
def records():
    return render_template('records.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    am = AutoMod()
    unmapped_services_list = am.get_services_in_no_web_maps()
    data_dict = {}
    for service in unmapped_services_list:
        data_dict[service.title] = service.owner
    data = {'message': data_dict}
    return jsonify(data)

@app.route('/api/user', methods=['GET'])
def get_user():
    am = AutoMod()
    inactive_users = am.get_inactive_users(return_type=list)
    data = {'message': inactive_users}
    return jsonify(data)

@app.route('/api/status', methods=['GET'])
def get_status():
    # Example data for "Status"
    logging.info(f'Sending http request to "maps.mercercounty.org/portal", "pip.mercercounty.org"')
    portal_status = handle_timeout('https://maps.mercercounty.org/portal',5, 'Timed out')
    pip_status = handle_timeout('http://pip.mercercounty.org/signin', 5, 'Timed out')
    agol_status = requests.get('https://mercernj.maps.arcgis.com/home/index.html', timeout=5).status_code
    data = {'message':
        {
        'maps.mercercounty.org/portal': f"Response: {str(portal_status)}",
        'pip.mercercounty.org/signin': f"Response: {str(pip_status)}",
        'mercernj.maps.arcgis.com/home': f"Response: {str(agol_status)}"
        }
    }
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


if __name__ == '__main__':
    app.run(debug=True)
