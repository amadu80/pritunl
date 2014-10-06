from pritunl.constants import *
from pritunl import utils
from pritunl.app_server import app_server
from pritunl import subscription
from pritunl import settings
import flask
import re

@app_server.app.route('/subscription', methods=['GET'])
@app_server.auth
def subscription_get():
    subscription.update()
    return utils.jsonify(subscription.dict())

@app_server.app.route('/subscription/state', methods=['GET'])
def subscription_state_get():
    return utils.jsonify({
        'active': settings.local.sub_active,
    })

@app_server.app.route('/subscription', methods=['POST'])
@app_server.auth
def subscription_post():
    license = flask.request.json['license']
    license = license.lower().replace('begin license', '').replace(
        'end license', '')
    license = re.sub(r'[\W_]+', '', license)

    try:
        response = utils.request.get(SUBSCRIPTION_SERVER,
            json_data={
                'license': license,
            },
        )
    except httplib.HTTPException:
        return utils.jsonify({
            'error': SUBSCRIPTION_SERVER_ERROR,
            'error_msg': SUBSCRIPTION_SERVER_ERROR_MSG,
        }, 500)
    data = response.json()

    if response.status_code != 200:
        return utils.jsonify(data, response.status_code)

    subscription.update_license(license)
    return utils.jsonify(subscription.dict())

@app_server.app.route('/subscription', methods=['PUT'])
@app_server.auth
def subscription_put():
    card = flask.request.json.get('card')
    email = flask.request.json.get('email')
    cancel = flask.request.json.get('cancel')

    try:
        if cancel:
            response = utils.request.delete(SUBSCRIPTION_SERVER,
                json_data={
                    'license': settings.app.license,
                },
            )
        else:
            response = utils.request.put(SUBSCRIPTION_SERVER,
                json_data={
                    'license': settings.app.license,
                    'card': card,
                    'email': email,
                },
            )
    except httplib.HTTPException:
        return utils.jsonify({
            'error': SUBSCRIPTION_SERVER_ERROR,
            'error_msg': SUBSCRIPTION_SERVER_ERROR_MSG,
        }, 500)

    if response.status_code != 200:
        return utils.jsonify(response.json(), response.status_code)

    subscription.update()
    return utils.jsonify(subscription.dict())

@app_server.app.route('/subscription', methods=['DELETE'])
@app_server.auth
def subscription_delete():
    subscription.update_license(None)
    return utils.jsonify({})
