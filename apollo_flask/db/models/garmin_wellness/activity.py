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
    
    start_time_local = Column(DateTime, 
            CheckConstraint("start_time_local > date '2019-01-01'",    
                name = "start_time_local_>_2019"), 
            primary_key = True)

    duration = Column(INTERVAL, CheckConstraint("duration > '0'::interval",
            name = "duration_gt_0"))
    
    avg_bike_cadence_rounds_per_minute = Column(Float,
         CheckConstraint("avg_bike_cadence_rounds_per_minute >= 0",
            name = "avg_bike_cadence >= 0"))
    max_bike_cadence_rounds_per_minute = Column(Float,
         CheckConstraint("max_bike_cadence_rounds_per_minute >=  \
            avg_bike_cadence_rounds_per_minute", name = "max_bike >= avg_bike"))

    avg_heart_rate = Column(Integer, CheckConstraint("avg_heart_rate >= 0",
        name = "avg_heart_rate >= 0"))
    max_heart_rate = Column(Integer, CheckConstraint("max_heart_rate >= \
         avg_heart_rate", name = "avg_hr >= max_hr"))

    avg_run_cadence_steps_per_minute = Column(Float, 
        CheckConstraint("avg_run_cadence_steps_per_minute >= 0",
            name = "avg_run_cadence >= 0"))
    max_run_cadence_steps_per_minute = Column(Float, 
        CheckConstraint("max_run_cadence_steps_per_minute >= \
            avg_run_cadence_steps_per_minute", name = "max_run_cadence >= avg")) 

    avg_speed_meters_per_second = Column(Float, 
        CheckConstraint("avg_speed_meters_per_second >= 0",
            name = "avg_speed > 0"))
    max_speed_meters_per_second = Column(Float,
        CheckConstraint("max_speed_meters_per_second >= \
            avg_speed_meters_per_second", 
            name = "max_speed >= avg"))

    avg_swim_cadence_strokes_per_minute = Column(Float,
        CheckConstraint("avg_swim_cadence_strokes_per_minute >= 0", 
            name= "avg_swim_cadence >= 0")) 
    
    avg_pace_minutes_per_km = Column(Integer, 
        CheckConstraint("avg_pace_minutes_per_km >= 0",
            name = "avg_pace_minutes_per_km >= 0"))
    max_pace_minutes_per_km = Column(Integer,
        CheckConstraint("max_pace_minutes_per_km <= \
            avg_pace_minutes_per_km", name= "max_pace <= avg_pace"))    

    active_kcal = Column(Integer, CheckConstraint("active_kcal >= 0",
        name = "active_kcal >= 0"))

    device_name = Column(String) #each device worn generates a different summay

    steps = Column(Integer, CheckConstraint("steps >= 0",
        name = "steps >= 0"))

    distance_meters = Column(Float, CheckConstraint("distance_meters >= 0",
        name = "distance >=0 "))

    number_of_active_lengths = Column(Integer, 
        CheckConstraint("number_of_active_lengths >= 0",
            name = "active_lengths >= 0"))

    starting_latitude_degrees = Column(Float, CheckConstraint(
        "starting_latitude_degrees > -90 AND starting_latitude_degrees < 90",
        name = "starting_latitude bounds"))
    starting_longitude_degrees = Column(Float, CheckConstraint(
        "starting_longitude_degrees > -180 AND \
        starting_longitude_degrees < 180", 
        name = "starting_longtitude bounds"))

    elevation_gain_total_meters = Column(Float, CheckConstraint(
        "elevation_gain_total_meters >= 0"))
    elevation_loss_total_meters = Column(Float, CheckConstraint(
        "elevation_loss_total_meters >= 0")) 

    ## NOTE: These two columns are apparently used for activities like "MULTI_SPORT", but 
    # I can't find any details on when they'd occur. The "MULTI_SPORT" activity itself is
    # undocumented. In addition, the "parent_summary_id" field in the 
    # API documentation is listed as "Integer", but summary ID's are strings.
    # Until this is resolved, I'm going to leave these commented out.
    # (It's probably for stuff like triathlon, where you have different activities happening 
    # within one session.  So I'm guessing they'd have a parent activity e.g. 'TRIATHLON'
    # with child activities like 'SWIMMING', 'CYCLING', etc.)
    
#    is_parent = Column(Boolean) #if this activity has child activities
#    parent_summary_id = Column(Integer) #present if the activity is a child acitivity
    
    manually_entered = Column(Boolean) #present if the acitivity was entered on the Connect website.

