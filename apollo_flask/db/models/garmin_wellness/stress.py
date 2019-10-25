from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Stress_Details(Base):
    """Stores stress and body battery summary metadata.
    All times in seconds."""

    __tablename__ = 'stress_details'
    __table_args__ = (UniqueConstraint('sid', 'start_time_utc'),
            UniqueConstraint('id'),
            {'schema':'garmin_wellness'})
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)
    
    start_time_utc = Column(DateTime, primary_key=True)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
