from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Stress_Sample(Base):
    """Stores stress details.
    All times in seconds."""

    __tablename__ = 'stress_sample'
    __table_args__ = {'schema':'garmin_wellness'}
    
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True) 
    time = Column(DateTime, primary_key = True)
    value = Column(Integer)
    
