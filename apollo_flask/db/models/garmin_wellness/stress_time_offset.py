from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Stress_Time_Offset(Base):
    """Stores stress details.
    All times in seconds."""

    __tablename__ = 'stress_time_offset'
    __table_args__ = {'schema':'garmin_wellness'}
    
    id = Column(Integer, ForeignKey('garmin_wellness.stress_details.id'), primary_key = True)
    
    time_offset = Column(INTERVAL, primary_key = True)
    value = Column(Integer)
    
