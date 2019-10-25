from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Heart_Rate_Samples_Time_Offset(Base):
    """Stores time-offset hear_rate_samples associated with a daily summary. """
    __tablename__ = 'heart_rate_samples_time_offset'
    __table_args__ = {'schema':'garmin_wellness'}

    id = Column(Integer, ForeignKey('garmin_wellness.daily_summary.id'), primary_key = True)

    time_offset = Column(INTERVAL, primary_key = True)
    value = Column(Integer)

