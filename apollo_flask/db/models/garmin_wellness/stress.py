from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Stress_Details(Base):
    """Stores stress and body battery details.
    All times in seconds."""

    __tablename__ = 'stress_details'
    __table_args__ = {'schema':'garmin_wellness'}
    
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key = True)
    
    start_time_utc = Column(DateTime, primary_key = True)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    
    stress_level_values_map = Column(JSON)
    body_battery_values_map = Column(JSON)

    
