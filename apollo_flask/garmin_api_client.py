"""This blueprint recieves data from the Garmin Wellness API push service."""
import functools

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
                calendar_date = dateutil.parser.parse(
                    summary.get('calendarDate')).date() if 
                    summary.get('calendarDate') is not None else None,
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

@bp.route('/mua', methods=['POST'])
def recieve_mua():
    pass

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
    pass

@bp.route('/body_comp', methods=['POST'])
def recieve_body_comp():
    pass

@bp.route('/tpd', methods=['POST'])
def recieve_tpd():
    pass

@bp.route('/stress', methods=['POST'])
def recieve_stress():
    pass

@bp.route('/user_metric', methods=['POST'])
def recieve_user_metric():
    pass

@bp.route('/moveiq', methods=['POST'])
def recieve_moveiq():
    pass

@bp.route('/pulseox', methods=['POST'])
def recieve_pulseox():
    pass


################################### Helper Functions ############################

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
                                table, 
                                incoming_data,
                                match_attr = 'summary_id',
                                order_attr = 'duration'):
    """[Parameters:]

        * session: Uses the session that is passed in (so another does
            not need to be created.)
        * table: The table in which we should look to find existing data
        * json_resp: The JSON response object that we are querying to determine if
            an update must occur.
        * match_attr (default: 'summaryId'): The attribute we should use 
            to match the incoming data with existing data.
        * order_attr (default: duration): The attribute that denotes which
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

    And so this is the criterion we operate on.
    """
    
    #We don't know the attribute we're matching on before runtime, so we've got 
    # to throw it in a dictionary and unpack when we hit our query.
    filter_by_kw = {match_attr : getattr(incoming_data,match_attr)}

    #Grab the existing data
    db_data = session.query(table).filter_by(**filter_by_kw).first()
            
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
