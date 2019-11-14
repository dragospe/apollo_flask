from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Epoch_Summary(Base):
    """Stores the summary data of a given epoch: a 15-minute interval snapshot of activities.
    Each epoch can contain multiple activities, and  thus multiple will often have the same start time and duration.
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'epoch_summary'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key = True)
    start_time_local = Column(DateTime, 
        CheckConstraint("start_time_local >= date '2019-01-01'", 
            name = "start_time >= 2019"),
        primary_key = True)

    duration = Column(INTERVAL, CheckConstraint("duration >= '0'::interval",
        name = "duration > 0"))
    active_time = Column(INTERVAL, CheckConstraint("active_time >= '0'::interval"))
    
    activity_type = Column(ACTIVITY_TYPE_ENUM)

    steps = Column(Integer, CheckConstraint("steps >= 0", name = "steps >= 0"))

    distance_meters = Column(Float, CheckConstraint("distance_meters >= 0", 
       name = "distance_meters >= 0")) 

    active_kcal = Column(Integer, CheckConstraint("active_kcal >= 0", 
        name = "active_kcal >= 0"))
    
    metabolic_equivalent_of_task = Column(Float, 
        CheckConstraint('metabolic_equivalent_of_task >= 0',
            name = 'm.e.t. >= 0'))
    
    intensity_qualifer = Column(WELLNESS_MONITORING_INTENSITY_ENUM)

    #See appendix D of the API spec
    mean_motion_intensity_score = Column(Float,
        CheckConstraint("mean_motion_intensity_score BETWEEN 0 AND 7",
            name = "mean_motion_intensity_score bounds"))
    max_motion_intensity_score = Column(Float,
        CheckConstraint("max_motion_intensity_score BETWEEN mean_motion_intensity_score AND 7",
            name = "max_motion_intensity_score bounds"))

