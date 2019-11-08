from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Sleep_Summary(Base):
    """Stores the summary data of a sleep period. See API spec for details.
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'sleep_summary'
    __table_args__ = (UniqueConstraint('sid','start_time_local'), UniqueConstraint('id'),
            {'schema':'garmin_wellness'})

    id = Column(Integer, primary_key = True, autoincrement=True)
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)

    start_time_local = Column(DateTime, 
        CheckConstraint("start_time_local >= '2019-01-01'", 
            name = "start_time >= 2019"),
        primary_key=True)

    duration = Column(INTERVAL, CheckConstraint("duration >= '0'::interval", 
        name = "duration > 0"))
    unmeasurable_sleep_time = Column(INTERVAL, 
        CheckConstraint("unmeasurable_sleep_time >= '0'::interval", 
        name = "unmeasureable_sleep > 0"))

    validation = Column(SLEEP_VALIDATION_ENUM)

