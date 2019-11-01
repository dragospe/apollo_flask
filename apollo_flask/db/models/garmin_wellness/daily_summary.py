from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Daily_Summary(Base):
    """Stores the daily activity summary. 
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'daily_summary'
    __table_args__ = ({'schema':'garmin_wellness'})


    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)

    start_time = Column(DateTime, primary_key=True)

    duration = Column(INTERVAL)
    steps = Column(Integer)
    distance_meters = Column(Float)
    active_time = Column(INTERVAL)

    active_kcal = Column(Integer)
    bmr_kcal = Column(Integer)
    consumed_cal = Column(Integer)

    moderate_intensity_duration = Column(INTERVAL) #in seconds from garmin
    vigorous_intensity_duration = Column(INTERVAL) 

    floors_climbed = Column(Integer)

    min_heart_rate = Column(Integer)
    avg_heart_rate = Column(Integer)
    max_heart_rate = Column(Integer)
    resting_heart_rate = Column(Integer)

    average_stress_level = Column(Integer)
    max_stress_level = Column(Integer)
    stress_duration = Column(INTERVAL)
    rest_stress_duration = Column(INTERVAL)
    activity_stress_duration = Column(INTERVAL)
    low_stress_duration = Column(INTERVAL)
    medium_stress_duration = Column(INTERVAL)
    high_stress_duration = Column(INTERVAL)
    stress_qualifier = Column(STRESS_QUALIFIER_ENUM)

    steps_goal = Column(Integer)
    net_kcal_goal = Column(Integer)
    intensity_duration_goal = Column(INTERVAL)
    floors_climbed_goal = Column(Integer)

