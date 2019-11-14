from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Stress_Sample(Base):
    """Stores stress details.
    All time_locals in seconds."""

    __tablename__ = 'stress_sample'
    __table_args__ = {'schema':'garmin_wellness'}
    
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True) 
    time_local = Column(DateTime, 
        CheckConstraint("time_local >= date '2019-01-01'",
            name = "time_local >= 2019"),
        primary_key = True)
    value = Column(Integer, CheckConstraint("value BETWEEN 0 AND 100",
        name = "stress value bounds"))
    
