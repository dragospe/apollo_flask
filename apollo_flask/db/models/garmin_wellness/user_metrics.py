from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import User_Id

class User_Metrics(Base):
    """Stores user metrics (VO2 Max and Fitness Age)."""

    __tablename__ = 'user_metrics'
    __table_args__ = {'schema': 'garmin_wellness'}

    user_metrics_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'))
    summary_id = Column(String, primary_key = True)

    calendar_date = Column(Date)

    vo2_max = Column(Float)
    fitness_age = Column(Integer)
