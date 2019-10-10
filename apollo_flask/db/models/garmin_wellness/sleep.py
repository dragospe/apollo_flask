from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class Sleep_Summary(Base):
    """Stores the summary data of a sleep period. See API spec for details.
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'sleep_summary'
    __table_args__ = {'schema':'garmin_wellness'}

    sleep_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'))

    summary_id = Column(String, primary_key = True)
    
    calendar_date = Column(Date)

    start_time = Column(DateTime)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    unmeasurable_sleep_time = Column(INTERVAL)

    deep_sleep_duration = Column(INTERVAL)
    light_sleep_duration = Column(INTERVAL)
    rem_sleep_duration = Column(INTERVAL)
    awake_duration = Column(INTERVAL)

    sleep_levels_map = Column(JSON)

    validation = Column(SLEEP_VALIDATION_ENUM)

    sleep_sp02_map = Column(JSON)
