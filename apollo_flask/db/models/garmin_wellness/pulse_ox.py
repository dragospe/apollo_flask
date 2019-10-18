from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class Pulse_Ox(Base):
    """Stores pulse-oxygen measurement data."""

    __tablename__ = "pulse_ox"
    __table_args__ = {'schema': 'garmin_wellness'}
    
    pulse_ox_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'), primary_key = True)

    start_time_utc = Column(DateTime, primary_key = True)
    start_time_offset = Column(INTERVAL)
    duration = Column(INTERVAL)

    #Time offset map
    spo2_value_map = Column(JSON)
    
    #Whether this is an 'on-demand' measurement or averaged acclimated reading
    on_demand = Column(Boolean)
