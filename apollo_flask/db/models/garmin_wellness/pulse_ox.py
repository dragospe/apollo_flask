from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Pulse_Ox(Base):
    """Stores pulse-oxygen measurement metadata."""

    __tablename__ = "pulse_ox"
    __table_args__ = (UniqueConstraint('sid', 'start_time_utc'),
            UniqueConstraint('id'),
         {'schema': 'garmin_wellness'})
    
    #Uniquely identify an API response to associate with the time offset map.
    id = Column(Integer, primary_key=True, autoincrement=True)

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key= True)
    start_time_utc = Column(DateTime, primary_key = True)

    start_time_offset = Column(INTERVAL)
    duration = Column(INTERVAL)

    #Whether this is an 'on-demand' measurement or averaged acclimated reading
    on_demand = Column(Boolean)
