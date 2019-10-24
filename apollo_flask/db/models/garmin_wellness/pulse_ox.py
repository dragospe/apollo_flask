from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Pulse_Ox(Base):
    """Stores pulse-oxygen measurement data."""

    __tablename__ = "pulse_ox"
    __table_args__ = {'schema': 'garmin_wellness'}
    
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key = True)

    start_time_utc = Column(DateTime, primary_key = True)
    start_time_offset = Column(INTERVAL)
    duration = Column(INTERVAL)

    #Time offset map
    spo2_value_map = Column(JSON)
    
    #Whether this is an 'on-demand' measurement or averaged acclimated reading
    on_demand = Column(Boolean)
