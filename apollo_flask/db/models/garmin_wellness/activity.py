from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class Activity_Summary(Base):
    """Stores the summary data of a given activity. 
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'activity_summary'
    __table_args__ = {'schema':'garmin_wellness'}

    activity_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'))

    summary_id = Column(String, primary_key = True)
    
    start_time = Column(DateTime)
    start_time_offset = Column(INTERVAL)

    duration = Column(Integer)
    
    avg_bike_cadence = Column(Float) #rounds per minute
    max_bike_cadence = Column(Float)

    avg_heart_rate = Column(Integer) #beats per minute
    max_heart_rate = Column(Integer)

    avg_run_cadence = Column(Float) #steps per minute
    max_run_cadence = Column(Float) #steps per minute

    avg_speed = Column(Float) #meters per second
    max_speed = Column(Float)

    avg_swim_cadence = Column(Float) #strokes per minute
    

    avg_pace = Column(Integer) #minutes per kilometer
    max_pace = Column(Integer)    

    active_kcal = Column(Integer)

    device_name = Column(String) #each device worn generates a different summay

    steps = Column(Integer)

    distance = Column(Float) #meters

    number_of_active_lengths = Column(Integer)

    starting_latitude = Column(Float) #In degrees; TODO: Change this to a GIS datatype?
    starting_longitude = Column(Float)

    elevation_gain = Column(Float) #total, in meters
    elevation_loss = Column(Float) #total

    ## NOTE: These two columns are apparently used for activities like "MULTI_SPORT", but 
    # I can't find any details on when they'd occur. The "MULTI_SPORT" activity itself is
    # undocumented. In addition, the "parent_summary_id" field in the 
    # API documentation is listed as "Integer", but summary ID's are strings.
    # Until this is resolved, I'm going to leave these commented out.
    
#    is_parent = Column(Boolean) #if this activity has child activities
#    parent_summary_id = Column(Integer) #present if the activity is a child acitivity
    
    manually_entered = Column(Boolean) #present if the acitivity was entered on the Connect website.

