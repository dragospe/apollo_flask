from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Heart_Rate_Sample(Base):
    """Stores time-offset heart_rate_samples associated with a daily summary. """
    __tablename__ = 'heart_rate_sample'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)

    time_local = Column(DateTime, 
        CheckConstraint("time_local >= date '2019-01-01'",
            name = "time_local > 2019"),
        primary_key = True)
    value = Column(Integer, 
        CheckConstraint("value >= 20 AND value <= 250",
            name = 'heart_rate bounds'))

