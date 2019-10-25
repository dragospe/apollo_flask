from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Pulse_Ox_Time_Offset(Base):
    """Stores pulse-oxygen measurement data."""

    __tablename__ = "pulse_ox_time_offset"
    __table_args__ = {'schema': 'garmin_wellness'}
    
    id = Column(Integer, ForeignKey('garmin_wellness.pulse_ox.id'), primary_key=True)

    time_offset = Column(INTERVAL, primary_key=True)
    value = Column(Integer)
