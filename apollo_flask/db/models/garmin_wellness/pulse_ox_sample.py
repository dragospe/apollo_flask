from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Pulse_Ox_Sample(Base):
    """Stores pulse-oxygen measurement data."""

    __tablename__ = "pulse_ox_sample"
    __table_args__ = {'schema': 'garmin_wellness'}
    
    id = Column(Integer, ForeignKey('garmin_wellness.pulse_ox.id'), primary_key=True)

    time_local = Column(DateTime, primary_key=True)
    value = Column(Integer)
