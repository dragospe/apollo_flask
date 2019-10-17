"""This blueprint recieves data from the Garmin Wellness API push service."""
import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

from apollo_flask.db import session_scope
from apollo_flask.db.models.garmin_wellness import *

from datetime import date, datetime, timedelta
import dateutil.parser

bp = Blueprint('garmin_api_client', __name__, url_prefix='/api_client/garmin')

@bp.route('/dailies', methods=['POST'])
def recieve_dailies():
    dailies = request.get_json()['dailies']
    with session_scope() as session:
        for summary in dailies:
            daily = daily_summary.Daily_Summary(
                daily_summary_uid = summary.get('userId'),
                summary_id = summary.get('summaryId'),
                calendar_date = get_calendar_date(summary),

                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
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
                time_offset_heart_rate_samples = summary.get('timeOffsetHeartRateSamples'),
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
            
            update_db_from_api_response(session, daily_summary.Daily_Summary, daily)

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
                activity_uid = summary.get('userId'),
                summary_id = summary.get('summaryId'),
                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
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
            update_db_from_api_response(session, activity.Activity_Summary, activity_summary)     
            
    return Response(status = 200)

@bp.route('/epochs', methods=['POST'])
def recieve_epochs():
    epochs = request.get_json()['epochs']
    with session_scope() as session:
        for summary in epochs:
            epoch_summary = epoch.Epoch_Summary(
                epoch_uid = summary.get('userId'),
                
                summary_id = summary.get('summaryId'),
                
                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
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

            update_db_from_api_response(session, epoch.Epoch_Summary, epoch_summary)     
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
                sleep_uid = summary.get('userId'),
                
                summary_id = summary.get('summaryId'),
                
                calendar_date = get_calendar_date(summary),
                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                
                duration = to_interval(summary.get('durationInSeconds')),
                unmeasurable_sleep_time = to_interval(summary.get('unmeasureableSleepInSeconds')),
                deep_sleep_duration = to_interval(summary.get(
                    'deepSleepDurationInSeconds')),
                light_sleep_duration = to_interval(summary.get(
                    'lightSleepDurationInSeconds')),   
                rem_sleep_duration = to_interval(summary.get('remSleepInSeconds')),
                awake_duration = to_interval(summary.get('awakeDurationInSeconds')),
                
                sleep_levels_map = summary.get('sleepLevelsMap'),
                validation = summary.get('validation'),
            
                sleep_sp02_map = summary.get('timeOffsetSleepSpo2')     
            )                

            db_sleep = session.query(sleep.Sleep_Summary).filter_by(calendar_date = sleep_summary.calendar_date).first()
            if db_sleep is not None:
                clone_row(sleep_summary, db_sleep)
            else:
                session.add(sleep_summary)

    return Response(status = 200)

@bp.route('/bodyComps', methods=['POST'])
def recieve_body_comp():
    body_comps = request.get_json()['bodyComps']
    with session_scope() as session:
        for summary in body_comps:
            bc = body_comp.Body_Composition(
                body_composition_uid = summary.get('UserId'),

                summary_id = summary.get('summaryId'),

                measurement_time = datetime.fromtimestamp(summary.get('measurementTimeInSeconds')),
                measurement_time_offset = to_interval(summary.get('measurementTimeOffsetInSeconds')),

                muscle_mass = summary.get('muscleMassInGrams'),
                bone_mass = summary.get('boneMassInGrams'),
            
                body_water_percentage = summary.get('bodyWaterInPercent'),
                body_fat_percentage = summary.get('bodyFatInPercent'),
                body_mass_index = summary.get('bodyMassIndex'),

                weight = summary.get('weightInGrams')
            )
            
            update_db_from_api_response(session, body_comp.Body_Composition, bc, match_attr= 'measurement_time', order_attr = 'measurement_time')

    return Response(status = 200)

@bp.route('/stressDetails', methods=['POST'])
def recieve_stress_details():
    stress_details = request.get_json()['stressDetails']
    with session_scope() as session:
        for summary in stress_details:
            stress_summary = stress.Stress_Details(
                stress_details_uid = summary.get('UserId'),
                summary_id = summary.get('summaryId'),
                
                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),                


                calendar_date = get_calendar_date(summary),
    
                stress_level_values_map = summary.get('timeOffsetStressLevelValues'),
                body_battery_values_map = summary.get('timeOffsetBodyBatteryDetails')
            )

            update_db_from_api_response(session, stress.Stress_Details, stress_summary,
                    match_attr='start_time', order_attr = 'duration')

    
    return Response(status = 200)


@bp.route('/userMetrics', methods=['POST'])
def recieve_user_metrics():
    user_metrics_summaries = request.get_json()['userMetrics']
    with session_scope() as session:
        for summary in user_metrics_summaries:
            metric_summary = user_metrics.User_Metrics(
                user_metrics_uid = summary.get('userId'),
                summary_id = summary.get('summaryId'),
        
                calendar_date = get_calendar_date(summary),
        
                vo2_max = summary.get('vo2Max'),
                fitness_age = summary.get('fitnessAge')
            )
            
            update_db_from_api_response(session, user_metrics.User_Metrics,
                 metric_summary, match_attr = 'calendar_date',
                 order_attr = 'calendar_date')

    return Response(status = 200)

@bp.route('/moveiq', methods=['POST'])
def recieve_moveiq():
    with open('json_dump', 'w') as f:
        json.dump(request.get_json(),f)

    move_iq_summaries = request.get_json()['moveIQActivities']
    with session_scope() as session:
        for summary in move_iq_summaries:
            move_iq_summary = move_iq.Move_Iq(
                
                move_iq_uid = summary.get('userId'),
                summary_id = summary.get('summaryId'),
                
                calendar_date = get_calendar_date(summary),

                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('offsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
    
                activity_type = summary.get('activityType'),
                activity_subtype = summary.get('activitySubType')
            )
            update_db_from_api_response(session, move_iq.Move_Iq, move_iq_summary, order_attr = 'duration')
                
    return Response(status = 200)

@bp.route('/pulseOx', methods=['POST'])
def recieve_pulseox():
    pulse_ox_summaries = request.get_json()['pulseox']
    with session_scope() as session:
        for summary in pulse_ox_summaries:
            pulse_ox_summary = pulse_ox.Pulse_Ox(
                pulse_ox_uid = summary.get('userId'),
                summary_id = summary.get('summaryId'),
                
                calendar_date = get_calendar_date(summary),
               
                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('offsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
                
                spo2_value_map = summary.get('timeOffsetSpo2Values'),
            
                on_demand = summary.get('OnDemand')
            )
    
            update_db_from_api_response(session, pulse_ox.Pulse_Ox, pulse_ox_summary)
    
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
                                table_obj, 
                                incoming_data,
                                match_attr = 'start_time',
                                order_attr = 'duration'):
    """[Parameters:]

        * session: Uses the session that is passed in (so another does
            not need to be created.)
        * table: The table in which we should look to find existing data
        * json_resp: The JSON response object that we are querying to determine if
            an update must occur.
        * match_attr (default: 'start_time'): The attribute we should use 
            to match the incoming data with existing data.
        * order_attr (default: 'duration'): The attribute that denotes which
            database object is more recent. If obj_1.order_attr < obj_2.order_attr,
            then obj_2 is considered more recent.

    [Background:] 

    When a JSON response is recieved from the garmin wellness API, it may
    include data that is already present in the database in some form. This 
    helper function should be used to streamline deciding whether or not the data
    that is present in the database matches any incoming data, and if so, whether
    the incoming data or the existing data is more recent, and updating as necessary.
    
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
   
    #We don't know the attribute we're matching on before runtime, so we've got 
    # to throw it in a dictionary and unpack when we hit our query.
    filter_by_kw = {match_attr : getattr(incoming_data,match_attr)}

    #Grab the existing data
    db_data = session.query(table_obj).filter_by(**filter_by_kw).first()
            
    if db_data is not None and \
            getattr(db_data, order_attr) <= getattr(incoming_data, order_attr):
        #The data already existed in the database, but the incoming data is more recent.
        clone_row(incoming_data, db_data)
    elif db_data is not None and \
            getattr(db_data, order_attr) > getattr(incoming_data, order_attr):
        #Existing data does not need to be updated
        pass
    else:
        #Incoming data did not already exist
        session.add(incoming_data)
