"""This blueprint recieves data from the Garmin Wellness API push service."""
import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

from apollo_flask.db import session_scope
from apollo_flask.db.models.garmin_wellness import *
from apollo_flask.db.models import Subject
from sqlalchemy.inspection import inspect

from datetime import date, datetime, timedelta
import dateutil.parser

bp = Blueprint('garmin_api_client', __name__, url_prefix='/api_client/garmin')

@bp.route('/dailies', methods=['POST'])
def recieve_dailies():
    dailies = request.get_json()['dailies']
    with session_scope() as session:
        for summary in dailies:
            daily = daily_summary.Daily_Summary(
                sid = uid2sid(session,summary.get('userId')),

                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
                steps = summary.get('steps'),
                distance = summary.get('distanceInMeters'),
                active_time = to_interval(summary.get('activeTimeInSeconds')),
                active_kcal = summary.get('activeKilocalories'),
                bmr_kcal = summary.get('bmrKilocalories'),
                consumed_cal = summary.get('consumedCalories'),
                moderate_intensity_duration = to_interval(
                        summary.get('moderateIntensityDurationInSeconds')),
                vigorous_intensity_duration = to_interval(
                        summary.get('vigorousIntensityDurationInSeconds')),
                floors_climbed = summary.get('floorsClimbed'),
                min_heart_rate = summary.get('minHeartRateInBeatsPerMinute'),
                avg_heart_rate = summary.get('averageHeartRateInBeatsPerMinute'),
                max_heart_rate = summary.get('maxHeartRateInBeatsPerMinute'),
                resting_heart_rate = summary.get('restingHeartRateInBeatsPerMinute'),
                average_stress = summary.get('averageStressLevel'),
                max_stress = summary.get('maxStressLevel'),
                stress_duration = to_interval(summary.get('stressDurationInSeconds')),
                rest_stress_duration = to_interval(summary.get('restStressDurationInSeconds')),
                activity_stress_duration = to_interval(
                        summary.get('activityStressDurationInSeconds')),
                low_stress_duration = to_interval(
                        summary.get('lowStressDurationInSeconds')),
                medium_stress_duration = to_interval(
                        summary.get('mediumStressDurationInSeconds')),
                high_stress_duration = to_interval(
                        summary.get('highStressDurationInSeconds')),
                stress_qualifier = summary.get('stressQualifier'),
                steps_goal = summary.get('stepsGoal') ,
                net_kcal_goal = summary.get('netKilocaloriesGoal'),
                intensity_duration_goal = to_interval(summary.get('intensityDurationGoal')),
                floors_climbed_goal = summary.get('floorsClimbedGoal'))
            
            update_db_from_api_response(session, daily, 'duration', 
                    time_offset_dict = {heart_rate_samples_time_offset.Heart_Rate_Samples_Time_Offset: summary.get('timeOffsetHeartRateSamples')})

    return Response(status=200)

@bp.route('/activities', methods=['POST'])
def recieve_activities():
    #NOTE: This is not (at this time) storing parent/child activity data, becuase
    # I can't find any documentation on this except that it may exist. See the
    # Garmin Wellness Activity_Summary data model for more details.
    activities = request.get_json()['activities']
    with session_scope() as session:
        for summary in activities:
            activity_summary = activity.Activity_Summary(
                sid = uid2sid(session,summary.get('userId')),
                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
                
                avg_bike_cadence = summary.get('averageBikeCadenceInRoundsPerMinute'),
                max_bike_cadence = summary.get('maxBikeCadenceInRoundsPerMinute'),
                
                avg_heart_rate = summary.get('averageHeartRateInBeatsPerMinute'),
                max_heart_rate = summary.get('maxHeartRateInBeatsPerMinute'),
            
                avg_run_cadence = summary.get('averageRunCadenceInStepsPerMinute'),
                max_run_cadence = summary.get('maxRunCadenceInStepsPerMinute'),

                avg_speed = summary.get('averageSpeedInMetersPerSecond'),
                max_speed = summary.get('maxSpeedInMetersPerSecond'),

                avg_swim_cadence = summary.get('averageSwimCadenceInStrokesPerMinute'),

                avg_pace = summary.get('averagePaceInMinutesPerKilometer'),
                max_pace = summary.get('maxPaceInMinutesPerKilometer'),
            
                active_kcal = summary.get('activeKilocalories'),
                
                device_name = summary.get('deviceName'),
        
                steps = summary.get('steps'),
                
                distance = summary.get('distanceInMeters'),
        
                number_of_active_lengths = summary.get('numberOfActiveLengths'),
                
                starting_latitude = summary.get('startingLatitudeInDegree'),
                starting_longitude = summary.get('startingLongitudeInDegree'),
                
                elevation_gain = summary.get('totalElevationGainInMeters'), 
                elevation_loss = summary.get('totalElevationLossInMeter'),

                #is_parent = ???
                #parent_summary_id = ???
                
                manually_entered = summary.get('manual'))
            update_db_from_api_response(session, activity_summary, 'duration')     
            
    return Response(status = 200)

@bp.route('/epochs', methods=['POST'])
def recieve_epochs():
    epochs = request.get_json()['epochs']
    with session_scope() as session:
        for summary in epochs:
            epoch_summary = epoch.Epoch_Summary(
                sid = uid2sid(session,summary.get('userId')),
                
                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                
                activity_type = summary.get('activityType'),

                duration = to_interval(summary.get('durationInSeconds')),
                activeTime = to_interval(summary.get('activeTimeInSeconds')),
    
                steps = summary.get('steps'),
                
                distance = summary.get('distanceInMeters'),
        
                active_kilocalories = summary.get('activeKilocalories'),

                met = summary.get('met'),

                mean_motion_intensity = summary.get('meanMotionIntensity'),
                max_motion_intensity = summary.get('maxMotionIntensity'))

            update_db_from_api_response(session, epoch_summary, 'duration')     
    return Response(status = 200)

@bp.route('/sleeps', methods=['POST'])
def recieve_sleeps():
    """For other data ingestion endpoints, there is a simple way to determine
    whether or not incoming data should create a new database record or update
    an existing one. For sleep data, this is not the case. The "validation" 
    of the JSON response gives some indication as to how "up-to-date" the data
    is, but is subject to change; further, the "AUTO_FINAL" and
    "ENHANCED_FINAL" validation types, which are meant to indicate that no 
    further changes to the data are expected, are not guaranteed to be sent.

    After emailing Garmin support, it appears that the current best way to
    update sleep data is to take the most recent response recieved.
    """
    sleeps = request.get_json()['sleeps']
    with session_scope() as session:
        for summary in sleeps:
            sleep_summary = sleep.Sleep_Summary(
                sid = uid2sid(session,summary.get('userId')),
                
                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                
                duration = to_interval(summary.get('durationInSeconds')),
                unmeasurable_sleep_time = to_interval(summary.get('unmeasureableSleepInSeconds')),
                deep_sleep_duration = to_interval(summary.get(
                    'deepSleepDurationInSeconds')),
                light_sleep_duration = to_interval(summary.get(
                    'lightSleepDurationInSeconds')),   
                rem_sleep_duration = to_interval(summary.get('remSleepInSeconds')),
                awake_duration = to_interval(summary.get('awakeDurationInSeconds')),
                
                validation = summary.get('validation'),
            
            )                

            #TODO: implement sleep levels time offset mapping.
            update_db_from_api_response(session, sleep_summary, 'duration')
           
    return Response(status = 200)

@bp.route('/bodyComps', methods=['POST'])
def recieve_body_comp():
    body_comps = request.get_json()['bodyComps']
    with session_scope() as session:
        for summary in body_comps:
            bc = body_comp.Body_Composition(
                sid = uid2sid(session,summary.get('userId')),

                measurement_time_utc = datetime.fromtimestamp(summary.get('measurementTimeInSeconds')),
                measurement_time_offset = to_interval(summary.get('measurementTimeOffsetInSeconds')),

                muscle_mass = summary.get('muscleMassInGrams'),
                bone_mass = summary.get('boneMassInGrams'),
            
                body_water_percentage = summary.get('bodyWaterInPercent'),
                body_fat_percentage = summary.get('bodyFatInPercent'),
                body_mass_index = summary.get('bodyMassIndex'),

                weight = summary.get('weightInGrams')
            )
            
            update_db_from_api_response(session,  bc, order_attr = 'measurement_time_utc')

    return Response(status = 200)

@bp.route('/stressDetails', methods=['POST'])
def recieve_stress_details():
    stress_details = request.get_json()['stressDetails']
    with session_scope() as session:
        for summary in stress_details:
            stress_summary = stress.Stress_Details(
                sid = uid2sid(session,summary.get('userId')),
                
                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),                
                )
            update_db_from_api_response(session, stress_summary, 'duration',
                    time_offset_dict = {body_battery_time_offset.Body_Battery_Time_Offset:
                                        summary.get('timeOffsetBodyBatteryValues'),
                                        stress_time_offset.Stress_Time_Offset:
                                        summary.get('timeOffsetStressLevelValues')})

    
    return Response(status = 200)


@bp.route('/userMetrics', methods=['POST'])
def recieve_user_metrics():
    user_metrics_summaries = request.get_json()['userMetrics']
    with session_scope() as session:
        for summary in user_metrics_summaries:
            metric_summary = user_metrics.User_Metrics(
                sid = uid2sid(session,summary.get('userId')),
        
                calendar_date = get_calendar_date(summary),
        
                vo2_max = summary.get('vo2Max'),
                fitness_age = summary.get('fitnessAge')
            )
            
            update_db_from_api_response(session, metric_summary, 'calendar_date')

    return Response(status = 200)

@bp.route('/moveiq', methods=['POST'])
def recieve_moveiq():

    move_iq_summaries = request.get_json()['moveIQActivities']
    with session_scope() as session:
        for summary in move_iq_summaries:
            move_iq_summary = move_iq.Move_Iq(
                sid = uid2sid(session,summary.get('userId')),

                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('offsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
    
                activity_type = summary.get('activityType'),
                activity_subtype = summary.get('activitySubType')
            )
            update_db_from_api_response(session, move_iq_summary, 'duration')
                
    return Response(status = 200)

@bp.route('/pulseOx', methods=['POST'])
def recieve_pulseox():
    pulse_ox_summaries = request.get_json()['pulseox']
    with session_scope() as session:
        for summary in pulse_ox_summaries:
            pulse_ox_summary = pulse_ox.Pulse_Ox(
                sid = uid2sid(session,summary.get('userId')),
                
                start_time_utc = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('offsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
           
                on_demand = summary.get('OnDemand')
            )
    
            update_db_from_api_response(session, pulse_ox_summary, 'duration',
                 time_offset_dict = {pulse_ox_time_offset.Pulse_Ox_Time_Offset : summary.get("timeOffsetSpo2Values")})
    
    return Response(status = 200)

################################### Helper Functions ############################
def get_calendar_date(summary):
    calendar_date = dateutil.parser.parse(summary.get('calendarDate')).date() if summary.get('calendarDate') is not None else None
    return calendar_date


def to_interval(x):
    """Helper function to convert the integers returned in the JSON respone to
    strings that can be turned into postgreSQL INTERVAL types."""
    if x == None:
        return None
    else:
        return timedelta(seconds = x) 

def clone_row(from_row, to_row):
    """Helper function to clone mapped objects IN PLACE. This helps we when take 
    the result of a query, and want to update it to match newer data."""
    
    for k in from_row.__table__.columns.keys():
        setattr(to_row,k, getattr(from_row,k))

def update_db_from_api_response(session, 
                                incoming_data,
                                order_attr,
                                time_offset_dict = None):
    """[Parameters:]

        * session: Uses the session that is passed in (so another does
            not need to be created.)
        * table: The table in which we should look to find existing data
        * json_resp: The JSON response object that we are querying to determine if
            an update must occur.
        * order_attr (default: 'duration'): The attribute that denotes which
            database object is more recent. If obj_1.order_attr < obj_2.order_attr,
            then obj_2 is considered more recent.
        * time_offset_dict: A dictionary containing a time offset Table and a time offset 
            value map, e.g. 
                {Pulse_Ox_Time_Offset}: { 0 : 94, 5 : 90, 10: 95}}
            Only necessary if the incoming data needs to be split into one or more
            time series tables.

    [Background:] 

    When a JSON response is recieved from the garmin wellness API, it may
    include data that is already present in the database in some form. This 
    helper function should be used to streamline deciding whether or not the data
    that is present in the database matches any incoming data, and if so, whether
    the incoming data or the existing data is more recent, and updating as necessary.
    It dynamically pulls the primary key for the passed in data and matches based on
    the attribute given in `order_attr`.
    
    In particular, section 6.1 of the Wellness REST API Specification states:

        "The Health API provides updates to previously issued summary records. 
        Updates are summary data records for a given user with the same start  
        time and summary type as a previous summary data record and a duration
        that is either equal to or greater than the previous summary data’s
        duration."

    And so this is the criterion we (generally) operate on. Certain summaries (e.g.
    sleep summaries) are ordered based on different criteria, and thus we allow
    some flexibility in the arguments to this method.
    """
    

    #Pack primary keys into a dictionary to be unpacked as kwargs
    pk_dict = {}
    for pk in inspect(incoming_data).class_.__mapper__.primary_key:
        pk_dict[pk.name] = getattr(incoming_data,pk.name)
    
    #Since the ID's are auto incremented, they aren't generated until an
    #object is added to the database. We remove them from pk_dict here
    #so that they don't cause an issue with filtering our query.
    pk_dict.pop('id', None)    

    #Grab class object
    class_obj = inspect(incoming_data).class_.__mapper__ 

    #Grab the existing data
    db_data = session.query(class_obj).filter_by(**pk_dict).one_or_none()
            
    if db_data is not None and \
            getattr(db_data, order_attr) <= getattr(incoming_data, order_attr):
        #The data already existed in the database, but the incoming data is more recent.
        #We copy the id from the database, overwrite the db_data, and then copy it's id 
        #back.
        db_id =  getattr(db_data,'id', None)
        clone_row(incoming_data, db_data)
        if db_id is not None:
            db_data.id=db_id
        session.commit()
        #Check if this is a time-offset-type summary, and update the time-offset data if so
        if time_offset_dict is not None:
            #Delete existing data
            delete_time_offsets_from_db(session, time_offset_dict, db_id)
            #Add new data
            add_time_offsets_to_db(session, time_offset_dict, db_id)
    elif db_data is not None and \
            getattr(db_data, order_attr) > getattr(incoming_data, order_attr):
        #Existing data does not need to be updated
        pass
    else:
        #Incoming data did not already exist. Add it
        session.add(incoming_data)      
        session.commit()
        if time_offset_dict is not None:
            add_time_offsets_to_db(session, time_offset_dict, incoming_data.id)        


def uid2sid(session, uid):
    """Convert user identifier to subject identifier using an existing
    session."""
    subject = session.query(Subject).filter_by(garmin_uid=uid).one_or_none()
    if (subject == None):
        return None
    return subject.subject_id


def add_time_offsets_to_db(session, time_offset_dict, fk_id):
    for Table in time_offset_dict:
        if time_offset_dict[Table] is None:
                #Since we are using .get instead of string indexing on our api
                #responses, time_offset_dict can contain None values. This just
                #means we didn't recieve data for that time period. Skip it and move on.
            continue
        for time_offset in time_offset_dict[Table]:
            time_offset_entry = Table(id = fk_id,
                                            time_offset = time_offset,
                                            value = time_offset_dict[Table][time_offset])
            session.add(time_offset_entry)


def delete_time_offsets_from_db(session, time_offset_dict, fk_id):
    for Table in time_offset_dict:
        if time_offset_dict[Table] is None:
                #Since we are using .get instead of string indexing on our api
                #responses, time_offset_dict can contain None values. This just
                #means we didn't recieve data for that time period. Skip it and move on.
            continue
        session.query(Table).filter_by(id =fk_id).delete()
