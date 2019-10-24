import pytest
import sqlalchemy
import apollo_flask.db
from apollo_flask.garmin_api_client import *
from apollo_flask.db.models.garmin_wellness import *
from apollo_flask.db.models.garmin_oauth import *
from apollo_flask.db.models.lib import *
from datetime import timedelta
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
    
    
    db_row = Dummy_Table(pk_attr = "123", attr1 = "db attr1", attr2 = 0,
        attr3 = False, attr4 = to_interval(100))
    recent_row = Dummy_Table(pk_attr = "123", attr1 = "recent attr1", attr2 = 1,
        attr3 = True, attr4 = to_interval(200))
    stale_row =  Dummy_Table(pk_attr = "123", attr1 = "stale attr1", attr2 = 2,
        attr3 = False, attr4 = to_interval(50))
    new_row = Dummy_Table(pk_attr = "456", attr1 = "new attr1")

    with session_scope() as session:
        #First add some data to the DB, then delete it from the session so we
        #start blank.
        session.add(db_row)
        session.commit()
        session.expunge(db_row)
        
        #Now update it with recent data
        update_db_from_api_response(session, recent_row, "attr4")
        
        query = session.query(Dummy_Table).filter_by(pk_attr = "123")
        
        #Only one result should have been returned    
        assert query.count() == 1, "Update from db_row to recent_row added multiple results."
        #Check that it contains the updated data
        assert query.first().attr1 == "recent attr1", "Update from db_row to recent_row"\
            " did not succeed in updating attr1."
        
        #Make sure stale rows don't overwrite recent rows
        update_db_from_api_response(session, stale_row, "attr4")

        #Only one result should have been returned    
        assert query.count() == 1, "Anti-Update from recent_row to stale_row added"\
            "multiple results."
        #Check that it contains the updated data
        assert query.first().attr1 == "recent attr1", "Anti-Update from to recent_row"\
            "changed attr1 when it shouldn't have."
         
        #Make sure new rows are added appropriately.
        update_db_from_api_response(session,  new_row, "attr4")

        query = session.query(Dummy_Table).filter_by(pk_attr = "456")
        
        #Make sure only one row was added
        assert query.count() == 1, "Multiple new rows added when new_row added."
        assert query.first().attr1 == "new attr1", "new_row attr1 not saved correctly."

        #All together now! We're going to wip the table, then
        # add the rows in random order, and make sure that only 
        #the proper rows remain at the end.
        import random

        for _ in range(10):
            #Wipe the table.
            session.query(Dummy_Table).delete()
            session.commit()
            assert session.query(Dummy_Table).count() == 0
            #Since these objects are deleted, we also need to remove them
            #from the session.
            session.expunge_all()
        
            #Recreate our rows (I think there's a better way to do this, but SQLalchemy
            #complains about detached objects if I don't.)
            db_row = Dummy_Table(pk_attr = "123", attr1 = "db attr1", attr2 = 0,
                attr3 = False, attr4 = to_interval(100))
            recent_row = Dummy_Table(pk_attr = "123", attr1 = "recent attr1", attr2 = 1,
                attr3 = True, attr4 = to_interval(200))
            stale_row =  Dummy_Table(pk_attr = "123", attr1 = "stale attr1", attr2 = 2,
                attr3 = False, attr4 = to_interval(50))
            new_row = Dummy_Table(pk_attr = "456", attr1 = "new attr1")



            ###Randomized testing from here out.
            row_list = [new_row, db_row, recent_row, stale_row]

            random.shuffle(row_list)
            
            for row in row_list:
                update_db_from_api_response(session, row, "attr4")

            assert session.query(Dummy_Table).count() == 2, "More than two rows added when only two should have been."
            assert session.query(Dummy_Table).filter_by(pk_attr = "456").first().attr1 == "new attr1"

            assert session.query(Dummy_Table).filter_by(pk_attr = "123").first().attr1 == "recent attr1"




########## test_recieve_* #####################
#The following tests are going to use some hardcoded data. They're mainly here to
#catch typos and make sure that endpoints are actually getting hit. Things may fail
#silently if there *are* typos, so these tests are going to try to minimize this.
#
#In each, we first add the user id of the user (the data all comes from the same user, namely myself) so that FK constraints don't nuke us
#when the test client POSTs json data.
#
#Feel free to approach with a better strategy.

def test_recieve_activities(client):
    with open('tests/garmin_api_responses/activities.json', 'r') as f:
         data = json.load(f)

    activities = data['activities']

    add_uids(activities)

    client.post('/api_client/garmin/activities',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_body_comps(client):
    with open('tests/garmin_api_responses/body_comps.json', 'r') as f:
         data = json.load(f)

    body_comps = data['bodyComps']

    add_uids(body_comps)

    client.post('/api_client/garmin/bodyComps',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_dailies(client):
    with open('tests/garmin_api_responses/dailies.json', 'r') as f:
         data = json.load(f)

    dailies = data['dailies']

    add_uids(dailies)

    client.post('/api_client/garmin/dailies',
                data= json.dumps(data),
                content_type = 'application/json')

def test_recieve_epochs(client):
    with open('tests/garmin_api_responses/epochs.json', 'r') as f:
         data = json.load(f)

    epochs = data['epochs']

    add_uids(epochs)

    client.post('/api_client/garmin/epochs',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_move_iq(client):
    with open('tests/garmin_api_responses/moveiq.json', 'r') as f:
         data = json.load(f)

    moveiq = data['moveIQActivities']

    add_uids(moveiq)

    client.post('/api_client/garmin/moveiq',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_pulse_ox(client):
    with open('tests/garmin_api_responses/pulse_ox.json', 'r') as f:
         data = json.load(f)

    pulseox = data['pulseox']

    add_uids(pulseox)

    client.post('/api_client/garmin/pulseOx',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_sleep(client):
    with open('tests/garmin_api_responses/sleeps.json', 'r') as f:
         data = json.load(f)

    sleeps = data['sleeps']

    add_uids(sleeps)

    client.post('/api_client/garmin/sleeps',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_stress(client):
    with open('tests/garmin_api_responses/stress_details.json', 'r') as f:
         data = json.load(f)

    stress_details = data['stressDetails']

    add_uids(stress_details)

    client.post('/api_client/garmin/StressDetails',
                data= json.dumps(data),
                content_type = 'application/json')


def test_recieve_user_metrics(client):
    with open('tests/garmin_api_responses/user_metrics_summaries.json', 'r') as f:
         data = json.load(f)

    user_metrics = data['userMetrics']

    add_uids(user_metrics)

    client.post('/api_client/garmin/UserMetrics',
                data= json.dumps(data),
                content_type = 'application/json')





############## Helpers ################
def add_uids(json_data):
    """Adds uids so the FK check passes in test_recieve_* tests."""
    with session_scope() as session:
        for summary in json_data:
            new_uid = User_Id(user_id = summary['userId'], 
                                active=True)
 
            #Check if UID exists in the db already
            db_uid = session.query(User_Id).filter_by(
                    user_id = new_uid.user_id).one_or_none()

            #Make sure its active if so
            if db_uid is not None:
                db_uid.active=True
            else: #Add it and an SID if not.
                session.add(new_uid)
                session.commit()
                subject = Subject(subject_id='Subject' + new_uid.user_id, 
                                  garmin_uid = new_uid.user_id)
                session.add(subject)
            


