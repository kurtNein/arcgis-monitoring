from flask import Flask, render_template, jsonify, request
from utils import AutoMod, EnterpriseMod
from smtplib import SMTP
import datetime
import json
import requests

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

@app.route('/portal.html')
def portal():
    return render_template('portal.html')

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
    for each in downloaded_items:
        print(each, downloaded_items[each])
        downloaded_items_formatted[f'{each}'] = str(downloaded_items[each])
        print(downloaded_items_formatted)
    data = {'message': downloaded_items_formatted}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
