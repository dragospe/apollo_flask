from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class Stress_Details(Base):
    """Stores stress and body battery details.
    All times in seconds."""

    __tablename__ = 'stress_details'
    __table_args__ = {'schema':'garmin_wellness'}
    
    stress_details_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'), primary_key = True)
    
    start_time_utc = Column(DateTime, primary_key = True)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    
    stress_level_values_map = Column(JSON)
    body_battery_values_map = Column(JSON)

    
