from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Sleep_Summary(Base):
    """Stores the summary data of a sleep period. See API spec for details.
    All time durations are given in seconds.
    Distances are given in meters.
    """
    __tablename__ = 'sleep_summary'
    __table_args__ = (UniqueConstraint('sid','start_time'), UniqueConstraint('id'),
            {'schema':'garmin_wellness'})

    id = Column(Integer, primary_key = True, autoincrement=True)
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)

    start_time = Column(DateTime, primary_key=True)

    duration = Column(INTERVAL)
    unmeasurable_sleep_time = Column(INTERVAL)

    validation = Column(SLEEP_VALIDATION_ENUM)

