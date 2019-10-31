from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Stress_Sample(Base):
    """Stores stress details.
    All times in seconds."""

    __tablename__ = 'stress_sample'
    __table_args__ = {'schema':'garmin_wellness'}
    
    id = Column(Integer, ForeignKey('garmin_wellness.stress_details.id'), primary_key = True)
    
    time_local = Column(DateTime, primary_key = True)
    value = Column(Integer)
    
