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



def test_recieve_dailies(client,app):
    #Some genuine data from the API data generator tool.
    #TODO: put this data in a separate file. Maybe make this test grab
    #arbitrary files from a particular directory, so that new testing data
    #can just be tossed in?
    dailies_dict = {'dailies' : [ {
  "summaryId" : "sd3114376-5d8cd915-15180-6",
  "activityType" : "WALKING",
  "activeKilocalories" : 100,
  "bmrKilocalories" : 7,
  "steps" : 988,
  "distanceInMeters" : 278.95,
  "durationInSeconds" : 86400,
  "activeTimeInSeconds" : 974,
  "startTimeInSeconds" : 1569511701,
  "startTimeOffsetInSeconds" : -18000,
  "moderateIntensityDurationInSeconds" : 4320,
  "vigorousIntensityDurationInSeconds" : 2100,
  "floorsClimbed" : 6,
  "minHeartRateInBeatsPerMinute" : 51,
  "maxHeartRateInBeatsPerMinute" : 72,
  "averageHeartRateInBeatsPerMinute" : 95,
  "restingHeartRateInBeatsPerMinute" : 47,
  "timeOffsetHeartRateSamples" : {
    "4873" : 51,
    "4936" : 68,
    "7801" : 65,
    "11614" : 64,
    "13686" : 72
  },
  "stepsGoal" : 6935,
  "netKilocaloriesGoal" : 18501,
  "intensityDurationGoalInSeconds" : 5700,
  "floorsClimbedGoal" : 20,
  "averageStressLevel" : 28,
  "maxStressLevel" : 14,
  "stressDurationInSeconds" : 905,
  "restStressDurationInSeconds" : 181,
  "activityStressDurationInSeconds" : 69,
  "lowStressDurationInSeconds" : 50,
  "mediumStressDurationInSeconds" : 67,
  "highStressDurationInSeconds" : 45
  }, {
  "summaryId" : "sd3114376-5d8e2a95-ef-6",
  "activityType" : "WALKING",
  "activeKilocalories" : 87,
  "bmrKilocalories" : 41,
  "steps" : 1057,
  "distanceInMeters" : 465.4,
  "durationInSeconds" : 239,
  "activeTimeInSeconds" : 218,
  "startTimeInSeconds" : 1569598101,
  "startTimeOffsetInSeconds" : -18000,
  "moderateIntensityDurationInSeconds" : 3840,
  "vigorousIntensityDurationInSeconds" : 1980,
  "floorsClimbed" : 5,
  "minHeartRateInBeatsPerMinute" : 51,
  "maxHeartRateInBeatsPerMinute" : 72,
  "averageHeartRateInBeatsPerMinute" : 52,
  "restingHeartRateInBeatsPerMinute" : 53,
  "timeOffsetHeartRateSamples" : {
    "4873" : 51,
    "4936" : 68,
    "7801" : 65,
    "11614" : 64,
    "13686" : 72
  },
  "stepsGoal" : 8454,
  "netKilocaloriesGoal" : 4583,
  "intensityDurationGoalInSeconds" : 6120,
  "floorsClimbedGoal" : 19,
  "averageStressLevel" : 36,
  "maxStressLevel" : 11,
  "stressDurationInSeconds" : 856,
  "restStressDurationInSeconds" : 148,
  "activityStressDurationInSeconds" : 60,
  "lowStressDurationInSeconds" : 56,
  "mediumStressDurationInSeconds" : 67,
  "highStressDurationInSeconds" : 48
  } ]}

    #Send the data
    client.post('/api_client/garmin/dailies', 
                data=json.dumps(dailies_dict), 
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
    #Define data
    activity_dict = {'activities': [ {'userId': '5c7d25f1-7580-4309-8e36-b00bce768ae5',
   'userAccessToken': 'f49f259b-a71b-4a28-a90b-fe7f0e1c7190',
   'summaryId': '13931969',
   'durationInSeconds': 5328,
   'startTimeInSeconds': 1568829554,
   'startTimeOffsetInSeconds': -18000,
   'activityType': 'WALKING',
   'averageHeartRateInBeatsPerMinute': 86,
   'averageRunCadenceInStepsPerMinute': 35.0,
   'averageSpeedInMetersPerSecond': 0.4819424,
   'averagePaceInMinutesPerKilometer': 18.423002,
   'activeKilocalories': 227,
   'distanceInMeters': 4682.99,
   'maxHeartRateInBeatsPerMinute': 126,
   'maxPaceInMinutesPerKilometer': 3.2194798,
   'maxRunCadenceInStepsPerMinute': 120.0,
   'maxSpeedInMetersPerSecond': 4.1503243,
   'steps': 1623,
   'totalElevationGainInMeters': 21.97},
  {'userId': '5c7d25f1-7580-4309-8e36-b00bce768ae5',
   'userAccessToken': 'f49f259b-a71b-4a28-a90b-fe7f0e1c7190',
   'summaryId': '14279282',
   'durationInSeconds': 4357,
   'startTimeInSeconds': 1568915954,
   'startTimeOffsetInSeconds': -18000,
   'activityType': 'WALKING',
   'averageHeartRateInBeatsPerMinute': 86,
   'averageRunCadenceInStepsPerMinute': 36.0,
   'averageSpeedInMetersPerSecond': 0.36856723,
   'averagePaceInMinutesPerKilometer': 18.140942,
   'activeKilocalories': 246,
   'distanceInMeters': 4475.72,
   'maxHeartRateInBeatsPerMinute': 140,
   'maxPaceInMinutesPerKilometer': 3.5551832,
   'maxRunCadenceInStepsPerMinute': 119.0,
   'maxSpeedInMetersPerSecond': 4.6923165,
   'steps': 1623,
   'totalElevationGainInMeters': 24.03} ] }

    #First add the appropriate user_id so that the Foriegn Key cosntraint holds
    with session_scope() as session:
        uid = User_Id(user_id = activity_dict['activities'][0]['userId'], active = True)
        session.add(uid)

    client.post('/api_client/garmin/activities', 
                data=json.dumps(activity_dict),
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

