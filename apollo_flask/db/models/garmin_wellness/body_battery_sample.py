from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Body_Battery_Sample(Base):
    """Stores body battery details.
    All times in seconds."""

    __tablename__ = 'body_battery_sample'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)
    time_local = Column(DateTime, 
        CheckConstraint("time_local > date '2019-01-01'", 
            name = "time_local > 2019"),
        primary_key = True)
    value = Column(Integer, CheckConstraint("value >= 0 AND value <= 100",
        name = "Body battery value bounds"))    
