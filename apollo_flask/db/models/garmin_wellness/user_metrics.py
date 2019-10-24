from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class User_Metrics(Base):
    """Stores user metrics (VO2 Max and Fitness Age)."""

    __tablename__ = 'user_metrics'
    __table_args__ = {'schema': 'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key = True)

    calendar_date = Column(Date, primary_key = True)

    vo2_max = Column(Float)
    fitness_age = Column(Integer)
