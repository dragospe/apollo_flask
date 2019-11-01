from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Heart_Rate_Sample(Base):
    """Stores time-offset hear_rate_samples associated with a daily summary. """
    __tablename__ = 'heart_rate_sample'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'), primary_key=True)

    time = Column(DateTime, primary_key = True)
    value = Column(Integer)

