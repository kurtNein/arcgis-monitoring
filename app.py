from flask import Flask, render_template, jsonify, request
from utils import AutoMod, EnterpriseMod
import json

app = Flask(__name__)

am = AutoMod()
em = EnterpriseMod()

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
    data = {'message': {'Status': 'Everything is running smoothly'}}
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
