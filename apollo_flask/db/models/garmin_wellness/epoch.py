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
    start_time = Column(DateTime, primary_key = True)

    duration = Column(INTERVAL)
    active_time = Column(INTERVAL) 
    
    activity_type = Column(ACTIVITY_TYPE_ENUM)

    steps = Column(Integer)

    distance_meters = Column(Float) 

    active_kcal = Column(Integer)
    
    met = Column(Float) #metabolic equivalent of task
    
    intensity_qualifer = Column(WELLNESS_MONITORING_INTENSITY_ENUM)

    mean_motion_intensity_score = Column(Float) #See appendix D of the API spec
    max_motion_intensity_score = Column(Float) #See appendix D of the API spec

