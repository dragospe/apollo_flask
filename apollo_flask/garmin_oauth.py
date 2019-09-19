#!/usr/bin/env python

################################### Imports: ###################################
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, Response
)

from rauth import OAuth1Service, OAuth1Session
import sys
import requests
import hashlib
import os
import time

from sqlalchemy.exc import IntegrityError

# The classes for the database objects
from apollo_flask.db.models.garmin_oauth import *
# Session, engine, and db helper functions
from apollo_flask.db import engine, session_scope

########################### Blueprint Declaration ##############################
bp = Blueprint('garmin_oauth', __name__, url_prefix='/oauth/garmin')

################################ Configuration: ################################

def get_garmin_oauth_service():
    garmin_oauth_service = OAuth1Service(
        consumer_key = current_app.config['GARMIN_CONSUMER_KEY'],
        consumer_secret = current_app.config['GARMIN_CONSUMER_SECRET'],
        name='garmin health',
        request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token', 
        authorize_url = 'https://connect.garmin.com/oauthConfirm',
        access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token',
        base_url = 'https://healthapi.garmin.com/wellness-api/rest')
    return garmin_oauth_service

############################### Pages/Functions: ###############################

@bp.route('/consent')
def request_user_access():
    """OAuth1, Step 1: Obtain a request token from the provider, and direct the 
    user to the appropriate authorization URL."""
    
    service = get_garmin_oauth_service()
    
    #Obtain and a request token and request token secret
    rt_pair = service.get_request_token()

    #Open a database session
    with session_scope() as session:
        request_token = Request_Token(
                        request_token = rt_pair[0], 
                        request_token_secret = rt_pair[1])     

        session.add(request_token)

        #Construct the authorization URL
        auth_url = service.get_authorize_url(request_token.request_token)
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    """OAuth 1, Step 2:  Receive authorization from the user.  This automatically
    triggers steps 3-4."""

    service = get_garmin_oauth_service()

    #Two query strings are passed back from the callback URL: a token and a 
    #verifier. The verifier must be returned as a query string when obtaining 
    #the access token.
    request_token  = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    
    if request_token==None or oauth_verifier==None :
        return Response(status=400)

    #Open a database session
    with session_scope() as session:
        #Match the request token from the request token secret.
        request_token_obj = session.query(Request_Token).filter_by(
            request_token=request_token).all()

        #Make sure only one secret was found; if not, respond 500. If so,
        #select it.
        try:
            if len(request_token_obj) > 1:
                raise Exception('There should only be one secret associated with\
                    the request token, but {} were found.'.format(
                    len(request_token_obj)))
        except:
            #TODO: double check this
            return Response(status= 500, response= '500 error:' + sys.exc_info())
        request_token_obj = request_token_obj[0]
        request_token_secret = request_token_obj.request_token_secret

        #Obtain the access token
        try:
            at_pair = service.get_access_token(
                request_token,
                request_token_secret,
                params={'oauth_verifier':oauth_verifier})
        except:
            return Response(status=500, response='500 error: Could not obtain access token')        

        #Every access token is associated with a user id. Fetch it:
        #Retry the request if it's failed; the garmin DB needs a second to update
        uid = User_Id(user_id = get_user_id(at_pair[0], at_pair[1]), active=True)
        #Check if the UID exists in the database
        db_uid = session.query(User_Id).filter_by(user_id= uid.user_id).first()
        if db_uid is not None:
            session.add(db_uid)
            db_uid.active=True 
        else:
            session.add(uid)

        #Save the access token/uid pair, checking if it exists first
        at = Access_Token(access_token=at_pair[0],
             access_token_secret=at_pair[1], user_id=uid.user_id)
        db_at = session.query(Access_Token).filter_by(
                    user_id= at.user_id).first()
        if db_at is not None:
            session.add(db_at)
            db_at.access_token = at.access_token
            db_at.access_token_secret = at.access_token_secret
        else:
            session.add(at)

        #We don't need the request token any more:
        session.delete(request_token_obj)

        #TODO: Make these responses better. Probably add error handling
        return Response(status = 202,
               response = "You have successfully authorized us to monitor your Garmin data.")

@bp.route('/deregistration', methods=['POST'])
def deregister_user():
    """Responds to a POST request containing a json dict listing the pending de-registrations"""
    deregs = request.get_json()['deregistrations']

    with session_scope() as session:
        for _ in deregs:
            #Set users to deactivated.
            user = session.query(User_Id).filter_by(user_id = _['userId']).first()
            session.add(user)
            user.active=False

            #Delete their access tokens.
            tokens = session.query(Access_Token).filter_by(user_id = _['userId']).all()
            for _ in tokens:
                session.delete(_)

    return 'Deregistered.'

def get_oauth_session(access_token, access_token_secret):
    """Helper function to return an authenticated session object for the given
    access token."""
    service = get_garmin_oauth_service()
    garmin_oauth_session = OAuth1Session(current_app.config['GARMIN_CONSUMER_KEY'], 
         current_app.config['GARMIN_CONSUMER_SECRET'],
         access_token, access_token_secret, service=service)
    return garmin_oauth_session


def get_user_id(access_token, access_token_secret):
    """Obtains the user id associated with a given access_token."""
    with  get_oauth_session(access_token, access_token_secret) as s:
        response = s.get('https://healthapi.garmin.com/wellness-api/rest/user/id',
                     header_auth=True) 

        #The garmin database takes a minute to update. If you don't get the
        #proper response, wait a bit and retry.
        tries = 0
        while ('userId' not in response.json()) and (tries < 3):
            response = s.get('https://healthapi.garmin.com/wellness-api/rest/user/id',
                     header_auth=True) 
            tries +=1
            #Sleep for a while
            time.sleep(tries)
        
        #Either we exceed our retries, or we have a uid.
        try:
            return response.json()['userId']
        except:
            raise("Could not get user ID.")
