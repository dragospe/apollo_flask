import pytest
import sqlalchemy
import apollo_flask.db
from apollo_flask.db.models.garmin_oauth import *
from apollo_flask.db.models.lib import *
import json
from conftest import add_uids

def test_degistration(client,app):
    with open('tests/garmin_api_responses/deregistration.json', 'r') as f:
        data = json.load(f)

    deregs = data['deregistrations']
    
    add_uids(deregs, app.session_scope)
    
    
    resp = client.post('/oauth/garmin/deregistration',
        data = json.dumps(data),
        content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/oauth/garmin/deregistration',
        data = json.dumps(data),
        content_type = 'application/json')
    assert resp.status_code == 200
