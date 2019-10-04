from apollo_flask.db.models.lib import *
from apollo_flask.db.models.garmin_oauth import *

class Move_Iq(Base):
    """Move_Iq is garmin's way of auto-detecting types of activities. They are
    not user editable. According to the garmin API spec, 

        "Wellness data, like steps and distance, from Move IQ events are
        already included in the Daily and Epoch summaries. [...] These events
        should be considered a labeled-timespane on top of normal Daily or Epoch
        summary details, matching their representation within Garmin Connect."
    """

    __tablename__ = 'move_iq'
    __table_args__ = {'schema':'garmin_wellness'}

    move_iq_uid = Column(String, ForeignKey('garmin_oauth.user_id.user_id'))
    summary_id = Column(String, primary_key = True)

    calendar_date = Column(DateTime)
    
    start_time = Column(DateTime)
    start_time_offset = Column(INTERVAL)

    duration = Column(INTERVAL)
    
    #Note: Activity (sub)types are either undocumented or just arbitrary; in
    #particular, they do not necessarily match those given in appendix A of the
    #API spec. Leaving these as datatype "String" for the time being.
    activity_type = Column(String)
    activity_subtype = Column(String)
    
