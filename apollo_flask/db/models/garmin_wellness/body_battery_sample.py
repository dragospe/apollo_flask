from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Body_Battery_Sample(Base):
    """Stores body battery details.
    All times in seconds."""

    __tablename__ = 'body_battery_sample'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)
    time = Column(DateTime, primary_key = True)
    value = Column(Integer)    
