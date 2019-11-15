import pytest
import sqlalchemy
import apollo_flask.db
from apollo_flask.garmin_api_client import *
from apollo_flask.db.models.garmin_wellness import *
from apollo_flask.db.models.garmin_oauth import *
from apollo_flask.db.models.lib import *
from datetime import timedelta
from conftest import add_uids
import json


class Dummy_Table(Base):
    """A table with some bogus data to help with testing."""
    __tablename__ = 'dummy_table'

    pk_attr = Column(String, primary_key=True)
    attr1 = Column(String)
    attr2 = Column(Integer)
    attr3 = Column(Boolean)
    attr4 = Column(INTERVAL)

    def __repr__(self):
        return "<Dummy Table: pk_attr = %s, attr1 = %s, attr2 = %s, attr3 = %s, attr4 = %s>"%(self.pk_attr, self.attr1, self.attr2, self.attr3, self.attr4) 

def test_to_interval():
    assert to_interval(None) == None, "to_interval(None) not working as expected."
    assert type(to_interval(100)) == timedelta
    assert to_interval(50) == timedelta(seconds=50)

def test_clone_row():
    """Make sure updating objects works how (you think) it should."""
    from_row = Dummy_Table(pk_attr = "From pk", attr1 = "From attr1", attr2 = 0,
        attr3 = False, attr4 = to_interval(100))
    to_row = Dummy_Table(pk_attr = "To pk", attr1 = "To attr1", attr2 = 1,
        attr3 = True, attr4 = to_interval(200))

    clone_row(from_row, to_row)

    assert to_row.pk_attr == "From pk", "clone_row failed on pk_attr (type: String)."
    assert to_row.attr1 == "From attr1", "clone_row failed on attr1 (type: String)."
    assert to_row.attr2 == 0, "clone_row failed on attr2 (type: Integer)"    
    assert to_row.attr3 == False, "clone_row failed on attr3 (type: Boolean)"
    assert to_row.attr4 == to_interval(100), "clone_row failed on attr4 (type: Interval)"

    assert to_row.pk_attr != "To pk", "clone_row failed on pk_attr (type: String)."
    assert to_row.attr1 != "To attr1", "clone_row failed on attr1 (type: String)."
    assert to_row.attr2 != 1, "clone_row failed on attr2 (type: Integer)"    
    assert to_row.attr3 != True, "clone_row failed on attr3 (type: Boolean)"
    assert to_row.attr4 != to_interval(200), "clone_row failed on attr4 (type: Interval)"

 
def test_update_db_from_api_response(app):
    """Put some dummy data in your dummy table, and then update it."""
    
    row1 = Dummy_Table(pk_attr = "123", attr1 = "1", attr2 = 1)
    row2 =  Dummy_Table(pk_attr = "123", attr1 = "2", attr3 = True)
    row3 = Dummy_Table(pk_attr = "456", attr1 = "3", attr2 = 3)

    with app.config['SESSION_SCOPE_FUNC']() as session:
        #firt row gets added to a blank db.
        update_db_from_api_response(session, row1)
        
        query_result = session.query(Dummy_Table).one()

        assert query_result.attr1 == "1", "row1.attr1 failed." 
        assert query_result.pk_attr == "123", "row1.pk_attr failed."
        assert query_result.attr2 == 1, "row1.attr2 failed."
    
        #second row should replace first row entirely
        update_db_from_api_response(session, row2)
        
        query_result = session.query(Dummy_Table).one()

        assert query_result.pk_attr == "123", "row2.pk_attr failed"
        assert query_result.attr1 == "2", "row2.attr1 failed"
        assert getattr(query_result,'attr2') == None, "row2.attr2 failed"
        assert query_result.attr3 == True, "row2.attr3 failed"

        #third row should not replace row 2, and should add its own row
        update_db_from_api_response(session, row3)

        query_result = session.query(Dummy_Table).filter_by(pk_attr = "123").one()

        assert query_result.pk_attr == "123", "Error in adding row3: row2.pk_attr modified."
        assert query_result.attr1 == "2", "Error in adding row3: row2.attr1 modified."
        assert getattr(query_result, 'attr2') == None, "Error in adding row3: row2.attr2 modified."
        assert query_result.attr3 == True, "Error in adding row3: row2.attr3 modified."

        query_result = session.query(Dummy_Table).filter_by(pk_attr = "456").one()
        
        assert query_result.pk_attr == "456", "row3.pk_attr failed"
        assert query_result.attr1 == "3",  "row3.attr1 failed"
        assert query_result.attr2 == 3, "row3.attr2 failed"




########## test_recieve_* #####################
#The following tests are going to use some hardcoded data. They're mainly here to
#catch typos and make sure that endpoints are actually getting hit. Things may fail
#silently if there *are* typos, so these tests are going to try to minimize this.
#
#In each, we first add the user id of the user (the data all comes from the same user, namely myself) so that FK constraints don't nuke us
#when the test client POSTs json data.
#
#Feel free to approach with a better strategy.

def test_recieve_activities(client, app):
    with open('tests/garmin_api_responses/activities.json', 'r') as f:
         data = json.load(f)

    activities = data['activities']

    add_uids(activities, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/activities',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/activities',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_body_comps(client, app):
    with open('tests/garmin_api_responses/body_comps.json', 'r') as f:
         data = json.load(f)

    body_comps = data['bodyComps']

    add_uids(body_comps, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/bodyComps',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/bodyComps',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_dailies(client, app):
    with open('tests/garmin_api_responses/dailies.json', 'r') as f:
         data = json.load(f)

    dailies = data['dailies']

    add_uids(dailies, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/dailies',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/dailies',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_epochs(client, app):
    with open('tests/garmin_api_responses/epochs.json', 'r') as f:
         data = json.load(f)

    epochs = data['epochs']

    add_uids(epochs, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/epochs',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/epochs',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_move_iq(client, app):
    with open('tests/garmin_api_responses/moveiq.json', 'r') as f:
         data = json.load(f)

    moveiq = data['moveIQActivities']

    add_uids(moveiq, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/moveiq',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/moveiq',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_pulse_ox(client, app):
    with open('tests/garmin_api_responses/pulse_ox.json', 'r') as f:
         data = json.load(f)

    pulseox = data['pulseox']

    add_uids(pulseox, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/pulseOx',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/pulseOx',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200



def test_recieve_sleep(client, app):
    with open('tests/garmin_api_responses/sleeps.json', 'r') as f:
         data = json.load(f)

    sleeps = data['sleeps']

    add_uids(sleeps, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/sleeps',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/sleeps',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_stress(client, app):
    with open('tests/garmin_api_responses/stress_details.json', 'r') as f:
         data = json.load(f)

    stress_details = data['stressDetails']

    add_uids(stress_details, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/stressDetails',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/stressDetails',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200

def test_recieve_user_metrics(client,app):
    with open('tests/garmin_api_responses/user_metrics_summaries.json', 'r') as f:
         data = json.load(f)

    user_metrics = data['userMetrics']

    add_uids(user_metrics, app.config['SESSION_SCOPE_FUNC'])

    resp = client.post('/api_client/garmin/userMetrics',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
    resp = client.post('/api_client/garmin/userMetrics',
                data= json.dumps(data),
                content_type = 'application/json')
    assert resp.status_code == 200
