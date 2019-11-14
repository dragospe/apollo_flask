from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Pulse_Ox_Sample(Base):
    """Stores pulse-oxygen measurement data."""

    __tablename__ = "pulse_ox_sample"
    __table_args__ = {'schema': 'garmin_wellness'}
    
    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)
    time_local = Column(DateTime, 
        CheckConstraint("time_local >= date '2019-01-01'",
            name = "time_local > 2019"),
        primary_key=True)

    value = Column(Integer, 
        CheckConstraint("value BETWEEN 0 and 100", name = "spo2 bounds"))
    on_demand = Column(Boolean)
