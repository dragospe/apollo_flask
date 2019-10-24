from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Sleep_Summary(Base):
    """Stores the summary data of a sleep period. See API spec for details.
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'sleep_summary'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key = True)

    start_time_utc = Column(DateTime, primary_key = True)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    unmeasurable_sleep_time = Column(INTERVAL)

    deep_sleep_duration = Column(INTERVAL)
    light_sleep_duration = Column(INTERVAL)
    rem_sleep_duration = Column(INTERVAL)
    awake_duration = Column(INTERVAL)

    sleep_levels_map = Column(JSON)

    validation = Column(SLEEP_VALIDATION_ENUM)

    sleep_spo2_map = Column(JSON)
