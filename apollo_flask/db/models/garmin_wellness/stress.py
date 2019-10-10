from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class Stress_Details(Base):
    """Stores stress and body battery details.
    All times in seconds."""

    __tablename__ = 'stress_details'
    __table_args__ = {'schema':'garmin_wellness'}
    
    stress_details_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'))
    
    summary_id = Column(String, primary_key = True)
    
    start_time = Column(DateTime)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    calendar_date = Column(Date)
    
    stress_level_values_map = Column(JSON)
    body_battery_values_map = Column(JSON)

    
