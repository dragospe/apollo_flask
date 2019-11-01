from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Activity_Summary(Base):
    """Stores the summary data of a given activity. 
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'activity_summary'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)
    
    start_time = Column(DateTime, primary_key = True)

    duration = Column(INTERVAL)
    
    avg_bike_cadence_rounds_per_minute = Column(Float) 
    max_bike_cadence_rounds_per_minute = Column(Float)

    avg_heart_rate = Column(Integer) 
    max_heart_rate = Column(Integer)

    avg_run_cadence_steps_per_minute = Column(Float) 
    max_run_cadence_steps_per_minute = Column(Float) 

    avg_speed_meters_per_second = Column(Float)
    max_speed_meters_per_second = Column(Float)

    avg_swim_cadence_strokes_per_minute = Column(Float) 
    

    avg_pace_minutes_per_km = Column(Integer) 
    max_pace_minutes_per_km = Column(Integer)    

    active_kcal = Column(Integer)

    device_name = Column(String) #each device worn generates a different summay

    steps = Column(Integer)

    distance_meters = Column(Float)

    number_of_active_lengths = Column(Integer)

    starting_latitude_degrees = Column(Float)
    starting_longitude_degrees = Column(Float)

    elevation_gain_total_meters = Column(Float)
    elevation_loss_total_meters = Column(Float) 

    ## NOTE: These two columns are apparently used for activities like "MULTI_SPORT", but 
    # I can't find any details on when they'd occur. The "MULTI_SPORT" activity itself is
    # undocumented. In addition, the "parent_summary_id" field in the 
    # API documentation is listed as "Integer", but summary ID's are strings.
    # Until this is resolved, I'm going to leave these commented out.
    
#    is_parent = Column(Boolean) #if this activity has child activities
#    parent_summary_id = Column(Integer) #present if the activity is a child acitivity
    
    manually_entered = Column(Boolean) #present if the acitivity was entered on the Connect website.

