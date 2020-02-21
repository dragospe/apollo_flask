from apollo_flask.db.models.lib import *
from . import garmin_oauth, garmin_wellness

class Subject(Base):
    """Contains data associated with a single participant of a study."""

    __tablename__ = 'subject'

    subject_id = Column(String, primary_key=True)
    garmin_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'), unique=True)

    def __repr__(self):
        return "<Subject(subject_id = '%s', garmin_uid = '%s')>"\
                %(self.subject_id, self.garmin_uid)
