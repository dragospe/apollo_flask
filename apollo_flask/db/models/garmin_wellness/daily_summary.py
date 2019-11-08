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

    start_time_local = Column(DateTime, 
        CheckConstraint("start_time_local >= date '2019-01-01'",
        name = "start_time >= 2019"),
        primary_key = True)

    duration = Column(INTERVAL, CheckConstraint("duration >= '0'::interval",
        name = "duration >= 0"))

    steps = Column(Integer, CheckConstraint("steps >= 0", name = "steps >= 0 "))
    distance_meters = Column(Float, CheckConstraint("distance_meters >= 0",
        name = "distance_meters >= 0"))
    active_time = Column(INTERVAL, CheckConstraint("active_time >= '0'::interval",
        name = "active_time >= 0"))

    active_kcal = Column(Integer, CheckConstraint("active_kcal >= 0", 
        name = "active_kcal >= 0"))
    bmr_kcal = Column(Integer, CheckConstraint("bmr_kcal >= 0",
        name = "bmr_kcal >= 0"))
    consumed_cal = Column(Integer, CheckConstraint("consumed_cal >= 0",
        name = "consumed_cal >= 0"))

    moderate_intensity_duration_seconds = Column(INTERVAL, 
        CheckConstraint("moderate_intensity_duration_seconds >= '0'::interval",
            name = "moderate_intensity >= 0")) 
    vigorous_intensity_duration_seconds = Column(INTERVAL,
        CheckConstraint("vigorous_intensity_duration_seconds >= '0'::interval",
            name = "vigoroous_intensity >= 0")) 

    floors_climbed = Column(Integer, CheckConstraint("floors_climbed >= 0",
        name = "floors_climbed >= 0"))

    min_heart_rate_for_monitoring_period = Column(Integer, 
        CheckConstraint("min_heart_rate_for_monitoring_period >= 0 ", 
            name = "min_heart_rate >= 0"))
    avg_heart_rate_for_week = Column(Integer,
        CheckConstraint("avg_heart_rate_for_week >= 0", 
            name = "avg_heart_rate_for_week >= 0"))
    max_heart_rate_for_monitoring_period = Column(Integer,
        CheckConstraint("max_heart_rate_for_monitoring_period >= \
            min_heart_rate_for_monitoring_period",
            name = "max_heart_rate >= min"))

    resting_heart_rate_for_monitoring_period = Column(Integer,
        CheckConstraint("resting_heart_rate_for_monitoring_period >= 0",
            name = "resting_heart_rate >= 0 "))

    average_stress_level = Column(Integer, 
        CheckConstraint("average_stress_level > 0", name= "avg_stress > 0 "))
    max_stress_level = Column(Integer,
        CheckConstraint("max_stress_level >= average_stress_level", 
            name = "max_stress_level"))
    stress_duration = Column(INTERVAL, CheckConstraint("stress_duration >= '0'::interval",
        name = "stress_duration >= 0"))
    rest_stress_duration = Column(INTERVAL, 
        CheckConstraint("rest_stress_duration >= '0'::interval",
            name = "rest_stress_duration >= 0"))
    activity_stress_duration = Column(INTERVAL,
        CheckConstraint("activity_stress_duration >= '0'::interval",
            name = "activity_stress_duration >= 0"))
    low_stress_duration = Column(INTERVAL, 
        CheckConstraint("low_stress_duration >= '0'::interval", 
            name = "low_stress_duration >= 0"))
    medium_stress_duration = Column(INTERVAL, 
        CheckConstraint("medium_stress_duration >= '0'::interval",
            name = "medium_stress_duration >= 0"))
    high_stress_duration = Column(INTERVAL, 
        CheckConstraint("high_stress_duration >= '0'::interval",
            name= "high_stress_duration >= 0"))
    stress_qualifier = Column(STRESS_QUALIFIER_ENUM)

    steps_goal = Column(Integer, CheckConstraint("steps_goal >= 0", 
        name = "steps_goal >= 0"))
    net_kcal_goal = Column(Integer, CheckConstraint("net_kcal_goal >= 0", 
        name = "net_kcal_goal >= 0"))
    intensity_duration_goal = Column(INTERVAL, 
        CheckConstraint("intensity_duration_goal >= '0'::interval",
            name = "intensity_duration_goal >= 0"))
    floors_climbed_goal = Column(Integer,
        CheckConstraint("floors_climbed_goal >= 0", 
            name = "floors_climbed_goal >= 0"))

