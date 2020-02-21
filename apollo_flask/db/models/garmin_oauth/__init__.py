"""Configuration for storing OAuth/OpenID data"""

################################## Classes: ###################################

class User_Id(Base):
    """From the 'Garmin Wellness REST API Specification':

        Each Garmin Connect user has a unique Health API ID associated with
        them that will persist across multiple UATs. For instance, if a user
        deletes their association through Garmin Connect and then, later,
        completes the OAuth process to generate a new User Access Token with
        the same Garmin Connect account, the second token will still have
        the same Health API User ID as the first token. Similarly, if a
        partner is managing multiple programs and the user signs up for each
        of them, the Health API User ID returned for each of the UATs will
        match.

        The Health API ID provides no identifying information and is not
        used in any other Garmin API, web service, or system. There is no
        reason to ever pass the Health API User ID back to the Health API
        as user lookup will always be performed using the User Access Token
        in the Authorization header.
    """

    __tablename__ = 'user_id'
    __table_args__ = {'schema':'garmin_oauth'}

    user_id = Column(String, primary_key=True)

    #Active unless a user has de-registered
    active = Column(Boolean, nullable=False)
    access_tokens = relationship('Access_Token')

    def __repr__(self):
        return "<Garmin_User_ID(user_id = '%s', access_tokens = '%s', active = '%s')>"\
                % (self.user_id, self.access_tokens, self.active)

class Request_Token(Base):
    """Stores a garmin OAuth1 request token and corresponding secret."""

    __tablename__ = 'request_token'
    __table_args__ = {'schema': 'garmin_oauth'}

    sid = Column(String, nullable=False)
    request_token = Column(String, primary_key=True)
    request_token_secret = Column(String, nullable=False)

class Access_Token(Base):
    """Stores an access token, corresponding secret, and the user id the
    token is authorized for."""
    __tablename__ = 'access_token'
    __table_args__ = {'schema' : 'garmin_oauth'}

    user_id = Column(
        String,
        ForeignKey('garmin_oauth.user_id.user_id'),
        primary_key=True)
    access_token = Column(String, primary_key=True)
    access_token_secret = Column(String, nullable=False)
    relationship('User_Id', back_populates='access_tokens')
