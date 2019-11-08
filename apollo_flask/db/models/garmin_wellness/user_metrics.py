from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class User_Metrics(Base):
    """Stores user metrics (VO2 Max and Fitness Age)."""

    __tablename__ = 'user_metrics'
    __table_args__ = {'schema': 'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key = True)

    calendar_date = Column(Date,
        CheckConstraint("calendar_date >= date '2019-01-01'",
            name = "calendar_date >= 2019"),
        primary_key = True)

    vo2_max_ml_per_min_per_kg = Column(Float,
        CheckConstraint('vo2_max_ml_per_min_per_kg <= 100 AND \
            vo2_max_ml_per_min_per_kg >= 0',
            name = "vo2_max bounds"))

    fitness_age = Column(Integer,
        CheckConstraint("fitness_age >= 0 AND fitness_age <= 110",
            name = "fitness_age bounds"))
