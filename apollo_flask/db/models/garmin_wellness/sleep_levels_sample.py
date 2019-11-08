from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Sleep_Levels_Sample(Base):
    """Stores sleep level details."""
    __tablename__ = 'sleep_levels_sample'
    __table_args__ = {'schema':'garmin_wellness'}

    id = Column(Integer, ForeignKey('garmin_wellness.sleep_summary.id'), primary_key=True)
    
    sleep_qualifier = Column(SLEEP_QUALIFIER_ENUM)
    start_time_local = Column(DateTime,
        CheckConstraint("start_time_local >= date '2019-01-01'",
            name = "start_time > 2019"),
        primary_key = True)
    duration = Column(INTERVAL, CheckConstraint("duration >= '0'::interval",
        name = "duration > 0"))

