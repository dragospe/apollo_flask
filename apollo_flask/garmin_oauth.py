#!/usr/bin/env python

################################### Imports: ###################################
import time

from flask import (
    Blueprint, redirect, render_template, request, current_app, Response
)

from rauth import OAuth1Service, OAuth1Session


# The classes for the database objects
from apollo_flask.db.models.garmin_oauth import *
from apollo_flask.db.models import Subject


########################### Blueprint Declaration ##############################
bp = Blueprint('garmin_oauth', __name__, url_prefix='/oauth/garmin')

################################ Configuration: ################################

def get_garmin_oauth_service():
    garmin_oauth_service = OAuth1Service(
        consumer_key=current_app.config['GARMIN_CONSUMER_KEY'],
        consumer_secret=current_app.config['GARMIN_CONSUMER_SECRET'],
        name='garmin health',
        request_token_url='https://connectapi.garmin.com/oauth-service/oauth/request_token',
        authorize_url='https://connect.garmin.com/oauthConfirm',
        access_token_url='https://connectapi.garmin.com/oauth-service/oauth/access_token',
        base_url='https://healthapi.garmin.com/wellness-api/rest')
    return garmin_oauth_service

############################### Pages/Functions: ###############################

@bp.route('/consent', methods=('GET', 'POST'))
def request_user_access():
    """OAuth1, Step 1: Have the user enter a RedCAP subject identifier.
    Obtain a request token from the provider, and direct the user to the
    appropriate authorization URL, saving the SID and request token in
    the database."""

    if request.method == 'POST':
        sid = request.form['sid']

        with current_app.session_scope() as session:
            db_sid = session.query(Subject).filter_by(subject_id=sid).one_or_none()
            if db_sid is not None:
                return render_template(
                    'oauth/garmin/consent.html',
                    sid_already_registered=sid,
                    project_name=current_app.config['PROJECT_NAME'])


            service = get_garmin_oauth_service()

            #Obtain and a request token and request token secret
            rt_pair = service.get_request_token()

            #Save the request token
            request_token = Request_Token(
                sid=sid,
                request_token=rt_pair[0],
                request_token_secret=rt_pair[1])

            session.add(request_token)

            #Construct the authorization URL
            auth_url = service.get_authorize_url(request_token.request_token)
        #Redirect the user to the garmin.com consent page.
        return redirect(auth_url)

    return render_template(
        'oauth/garmin/consent.html',
        project_name=current_app.config['PROJECT_NAME'])

@bp.route('/callback')
def callback():
    """OAuth 1, Step 2:  Receive authorization from the user.  This automatically
    triggers steps 3-4."""

    service = get_garmin_oauth_service()

    #Two query strings are passed back from the callback URL: a token and a
    #verifier. The verifier must be returned as a query string when obtaining
    #the access token.
    request_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    if request_token is None or oauth_verifier is None:
        return Response(status=400)

    #Open a database session
    with current_app.session_scope() as session:
        #Match the request token from the request token secret.
        rt = session.query(Request_Token).filter_by(
            request_token=request_token).one_or_none()

        #Obtain the access token
        try:
            at_pair = service.get_access_token(
                request_token,
                rt.request_token_secret,
                params={'oauth_verifier':oauth_verifier})
        except:
            return Response(status=500, response='500 error: Could not obtain access token')

        #Every access token is associated with a user id. Fetch it:
        #Retry the request if it's failed; the garmin DB needs a second to update
        uid = User_Id(user_id=get_user_id(at_pair[0], at_pair[1]), active=True)

        #Check if the UID or an associated SID exists in the database. If not, add them.
        db_uid = session.query(User_Id).filter_by(user_id=uid.user_id).one_or_none()
        db_sid = session.query(Subject).filter_by(subject_id=rt.sid).one_or_none()
        db_subject_uid = session.query(Subject).filter_by(garmin_uid=uid.user_id).one_or_none()

        #Check if the SID from the db is already associated with a different garmin UID
        if db_sid is not None and db_sid.garmin_uid != uid.user_id:
            return Response(
                status=409,
                response=\
                    render_template(
                        'oauth/garmin/callback.html',
                        sid_already_associated=rt.sid,
                        project_name=current_app.config['PROJECT_NAME']))

        #Check if the garmin account in question is already associated with a different SID
        if db_sid is None and db_subject_uid is not None:
            return Response(
                status=409,
                response=\
                    render_template(
                        'oauth/garmin/callback.html',
                        uid_already_associated_with_sid=db_subject_uid,
                        project_name=current_app.config['PROJECT_NAME']))

        #If the garmin account exists, but is inactive, make it active
        elif db_uid is not None:
            db_uid.active = True
        #If the garmin UID does not exist in the database, add it.
        elif db_uid is None:
            session.add(uid)
            session.commit()
        #If the SID does not exist in the database, add it.
        elif db_sid is None:
            subject = Subject(subject_id=rt.sid, garmin_uid=uid.user_id)
            session.add(subject)

        #Save the access token/uid pair, checking if it exists first
        at = Access_Token(
            access_token=at_pair[0],
            access_token_secret=at_pair[1],
            user_id=uid.user_id)
        db_at = session.query(Access_Token).filter_by(
            user_id=at.user_id).first()
        if db_at is not None:
            session.add(db_at)
            db_at.access_token = at.access_token
            db_at.access_token_secret = at.access_token_secret
        else:
            session.add(at)

        #We don't need the request token any more:
        sid = rt.sid
        session.delete(rt)


    return Response(
        status=202,
        response=render_template(
            'oauth/garmin/callback.html',
            sid_success=sid,
            project_name=current_app.config['PROJECT_NAME']))

@bp.route('/deregistration', methods=['POST'])
def deregister_user():
    """Responds to a POST request containing a json dict listing the pending de-registrations"""
    deregs = request.get_json()['deregistrations']

    with current_app.session_scope() as session:
        for _ in deregs:
            #Set users to deactivated.
            user = session.query(User_Id).filter_by(user_id=_['userId']).one_or_none()
            if user is not None:
                session.add(user)
                user.active = False
            else:
                current_app.logger.info('Deregistration for use %s recieved,\
                    but user does not exist.', _['userId'])

            #Delete their access tokens.
            tokens = session.query(Access_Token).filter_by(user_id=_['userId']).all()
            for token in tokens:
                if token is not None:
                    session.delete(token)

    return Response(status=200)

def get_oauth_session(access_token, access_token_secret):
    """Helper function to return an authenticated session object for the given
    access token."""
    service = get_garmin_oauth_service()
    garmin_oauth_session =\
         OAuth1Session(
             current_app.config['GARMIN_CONSUMER_KEY'],
             current_app.config['GARMIN_CONSUMER_SECRET'],
             access_token,
             access_token_secret,
             service=service)

    return garmin_oauth_session


def get_user_id(access_token, access_token_secret):
    """Obtains the user id associated with a given access_token."""
    with  get_oauth_session(access_token, access_token_secret) as s:
        response = s.get(
            'https://healthapi.garmin.com/wellness-api/rest/user/id',
            header_auth=True)

        #The garmin database takes a minute to update. If you don't get the
        #proper response, wait a bit and retry.
        tries = 0
        while ('userId' not in response.json()) and (tries < 3):
            response = s.get(
                'https://healthapi.garmin.com/wellness-api/rest/user/id',
                header_auth=True)
            tries += 1
            #Sleep for a while
            time.sleep(tries)

        #Either we exceed our retries, or we have a uid.
        try:
            return response.json()['userId']
        except:
            raise "Could not get user ID."
