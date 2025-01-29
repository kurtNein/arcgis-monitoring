from flask import Flask, render_template, jsonify, request
from utils import AutoMod


app = Flask(__name__)

am = AutoMod()


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


if __name__ == '__main__':
    app.run(debug=True)
