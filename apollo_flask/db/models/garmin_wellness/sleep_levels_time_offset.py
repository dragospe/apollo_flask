from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Sleep_Levels_Time_Offset(Base):
    """Stores sleep level details..
    """
    __tablename__ = 'sleep_levels_time_offset'
    __table_args__ = {'schema':'garmin_wellness'}

    id = Column(Integer, ForeignKey('garmin_wellness.sleep_summary.id'), primary_key=True)
    
    time_offset = Column(INTERVAL, primary_key = True)
    value = Column(Integer)
