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
        update_db_from_api_response(session, Dummy_Table, recent_row, 
                match_attr = "pk_attr", order_attr = "attr4")
        
        query = session.query(Dummy_Table).filter_by(pk_attr = "123")
        
        #Only one result should have been returned    
        assert query.count() == 1, "Update from db_row to recent_row added multiple results."
        #Check that it contains the updated data
        assert query.first().attr1 == "recent attr1", "Update from db_row to recent_row"\
            " did not succeed in updating attr1."
        
        #Make sure stale rows don't overwrite recent rows
        update_db_from_api_response(session, Dummy_Table, stale_row,
                match_attr = "pk_attr", order_attr = "attr4")

        #Only one result should have been returned    
        assert query.count() == 1, "Anti-Update from recent_row to stale_row added"\
            "multiple results."
        #Check that it contains the updated data
        assert query.first().attr1 == "recent attr1", "Anti-Update from to recent_row"\
            "changed attr1 when it shouldn't have."
         
        #Make sure new rows are added appropriately.
        update_db_from_api_response(session, Dummy_Table, new_row, match_attr = "pk_attr",
                order_attr = "attr4")

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

            row_list = [new_row, db_row, recent_row, stale_row]

            random.shuffle(row_list)
            
            for row in row_list:
                update_db_from_api_response(session, 
                                Dummy_Table, 
                                row, 
                                match_attr = "pk_attr",
                                order_attr = "attr4")

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



#Load a big ball of JSON so that we can test out recieving 
#   data from garmin."""
with open('tests/garmin_api_mega_response_data', 'rb') as f:
        garmin_api_mega_response = json.load(f)


def test_recieve_dailies(client,app):
    add_dummy_user()

    #Send the data
    client.post('/api_client/garmin/dailies', 
                data = json.dumps(garmin_api_mega_response),
                content_type='application/json')

    #Ensure the data got put in:
    #TODO: Test on more attributes? This might be a PITA the way I did it.
    with session_scope() as session:
        query = session.query(daily_summary.Daily_Summary)
        assert query.count() == 2, "Exactly two dailies were not added."
       
        summary1 =  query.filter_by(summary_id = "sd3114376-5d8cd915-15180-6").first()
        assert summary1.start_time == datetime.fromtimestamp(1569511701)
        
        summary2 =  query.filter_by(summary_id = "sd3114376-5d8e2a95-ef-6").first()
        assert summary2.start_time == datetime.fromtimestamp(1569598101)
    
def test_recieve_activities(client, app):
    add_dummy_user() 

    client.post('/api_client/garmin/activities', 
                data = json.dumps(garmin_api_mega_response),
                content_type = 'application/json')

    #Ensure the data got put in:
    #TODO: Test on more attributes? This might be a PITA the way I did it.
    with session_scope() as session:
        query = session.query(activity.Activity_Summary)
        assert query.count() == 2, "Exactly 2 activities  were not added."
       
        activity1 =  query.filter_by(summary_id = "13931969").first()
        assert activity1.start_time == datetime.fromtimestamp(1568829554)
        
        summary2 =  query.filter_by(summary_id = "14279282").first()
        assert summary2.start_time == datetime.fromtimestamp(1568915954)

def test_recieve_epochs(client, app):
    add_dummy_user()

    client.post('/api_client/garmin/epochs',
                data=json.dumps(garmin_api_mega_response),
                content_type = 'application/json')

    with session_scope() as session:
        query = session.query(epoch.Epoch_Summary)
        assert query.count() >= 1, "No epochs were added."
       
        epoch1 =  query.filter_by(summary_id = "sd3114376-5d8d0382-8").first()
        assert epoch1.start_time == datetime.fromtimestamp( 1569522562)
        
        epoch2 =  query.filter_by(summary_id = "sd3114376-5d8cf8f6-6").first()
        assert epoch2.start_time == datetime.fromtimestamp(1569519862)

#def test_recieve_sleep(client, app):
    #Add the user
    #with session_scope() as session: 
    #    uid = User_Id(user_id = "5c7d25f1-7580-4309-8e36-b00bce768ae5", active = True)
    #    session.add(uid)

    #client.post('/api_client/garmin/sleeps',
    #            data=json.dumps(garmin_api_mega_response),
    #            content_type = 'application/json')

    #with session_scope() as session:
    #    query = session.query(sleep.Sleep_Summary)
    #    assert query.count() == 8, "Exactly 8 sleeps were not added."
       
    #    sleep1 =  query.filter_by(summary_id = "d3114376-5d8d7aaf-9396").first()
    #    assert sleep1.start_time == datetime.fromtimestamp(1569553071)
        
    #    sleep2 =  query.filter_by(summary_id = 'x3114376-5d5fb86c-4dd0').first()
    #    assert sleep2.start_time == datetime.fromtimestamp(1566554220)

def test_recieve_body_comps(client, app):
    add_dummy_user()
    client.post('/api_client/garmin/bodyComps',
                data=json.dumps(garmin_api_mega_response),
                content_type = 'application/json')

    with session_scope() as session:
        query = session.query(body_comp.Body_Composition)
        assert query.count() == 1, "Exactly 1 body comp was not added."
       
        bc1 =  query.filter_by(summary_id = "x3114376-5d9754d4").first()
        assert bc1.weight == 90718
        

def test_recieve_stress(client, app):
    add_dummy_user()

    client.post('/api_client/garmin/stressDetails',
                data=json.dumps(garmin_api_mega_response),
                content_type = 'application/json')
    
    with session_scope() as session:
        query = session.query(stress.Stress_Details)
        assert query.count() == 2, "Exactly 2 stress details were not added."
        
        stress1 = query.filter_by(summary_id = "sd3114376-5d961996-232").first()
        assert stress1.start_time == datetime.fromtimestamp(1570118038)

        stress2 = query.filter_by(start_time = datetime.fromtimestamp(1570204438)).first()
        assert stress2.stress_level_values_map['141'] == 30

def test_receive_user_metrics(client, app):
    add_dummy_user()
    client.post('/api_client/garmin/userMetrics',
            data=json.dumps(garmin_api_mega_response),
            content_type = 'application/json')
    
    with session_scope() as session:
        query = session.query(user_metrics.User_Metrics)
        assert query.count() == 2, "Exactly 2 user metrics summaries were not added."
        
        um1 = query.filter_by(summary_id = "sd3114376-5d961996").first()
        assert um1.vo2_max == 42

        um2 = query.filter_by(summary_id = 'sd3114376-5d976b16').first()
        assert um2.fitness_age == 60

def test_receive_move_iq(client, app):
    add_dummy_user()
    client.post('/api_client/garmin/moveiq',
            data=json.dumps(garmin_api_mega_response),
            content_type = 'application/json')
    
    with session_scope() as session:
        query = session.query(move_iq.Move_Iq)
        assert query.count() == 2, "Exactly 2 move iq summaries were not added."
       
        miq1 = query.filter_by(summary_id = 'sd3114376-5d961996Running2d').first()
        assert miq1.activity_type == "Running"

def test_receive_pulse_ox(client, app):
    add_dummy_user()
    client.post('/api_client/garmin/pulseOx',
            data=json.dumps(garmin_api_mega_response),
            content_type = 'application/json')

    with session_scope() as session:
        query = session.query(pulse_ox.Pulse_Ox)
        assert query.count() == 2, "Exactly 2 pulse ox measurements were not added."
        
        po1 = query.filter_by(summary_id = 'sd3114376-5d976b16').first()
        assert po1.spo2_value_map['0']==100


#### Helpers ####
def add_dummy_user():
    with session_scope() as session: 
        uid = User_Id(user_id = "5c7d25f1-7580-4309-8e36-b00bce768ae5", active = True)
        session.add(uid)


