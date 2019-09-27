from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class Epoch_Summary(Base):
    """Stores the summary data of a given epoch: a 15-minute interval snapshot of activities.
    Each epoch can contain multiple activities, and  thus multiple will often have the same start time and duration.
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'epoch_summary'
    __table_args__ = {'schema':'garmin_wellness'}

    epoch_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'))

    summary_id = Column(String, primary_key = True)
    
    start_time = Column(DateTime)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    activeTime = Column(INTERVAL) 
    
    activity_type = Column(ACTIVITY_TYPE_ENUM)

    steps = Column(Integer)

    distance = Column(Float) #meters

    active_kilocalories = Column(Integer)
    
    met = Column(Float) #metabolic equivalent of task
    
    intensity = Column(WELLNESS_MONITORING_INTENSITY_ENUM)

    mean_motion_intensity = Column(Float) #See appendix D of the API spec
    max_motion_intensity = Column(Float) #See appendix D of the API spec

