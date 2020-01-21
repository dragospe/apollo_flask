"""This blueprint recieves data from the Garmin Wellness API push service."""
import functools
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    Response, current_app
)

from apollo_flask.db.models.garmin_wellness import *
from apollo_flask.db.models import Subject
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import text

from datetime import date, datetime, timedelta
import dateutil.parser

bp = Blueprint('garmin_api_client', __name__, url_prefix='/api_client/garmin')



@bp.route('/dailies', methods=['POST'])
def recieve_dailies():
    dailies = request.get_json()['dailies']
    with current_app.session_scope() as session:
        for summary in dailies:
            daily = daily_summary.Daily_Summary(
                sid = uid2sid(session,summary.get('userId')),

                start_time_local = datetime.fromtimestamp(summary.get('startTimeInSeconds') +
                         summary.get('startTimeOffsetInSeconds')),

                duration = to_interval(summary.get('durationInSeconds')),
                steps = summary.get('steps'),
                distance_meters = summary.get('distanceInMeters'),
                active_time = to_interval(summary.get('activeTimeInSeconds')),

                active_kcal = summary.get('activeKilocalories'),
                bmr_kcal = summary.get('bmrKilocalories'),
                consumed_cal = summary.get('consumedCalories'),

                moderate_intensity_duration_seconds = to_interval(
                        summary.get('moderateIntensityDurationInSeconds')),
                vigorous_intensity_duration_seconds = to_interval(
                        summary.get('vigorousIntensityDurationInSeconds')),
          
                floors_climbed = summary.get('floorsClimbed'),
           
                min_heart_rate_for_monitoring_period = summary.get(
                    'minHeartRateInBeatsPerMinute'),
                avg_heart_rate_for_week = summary.get(
                    'averageHeartRateInBeatsPerMinute'),
                max_heart_rate_for_monitoring_period = summary.get(
                    'maxHeartRateInBeatsPerMinute'),
                resting_heart_rate_for_monitoring_period = summary.get(
                    'restingHeartRateInBeatsPerMinute'),
            
                # Stress levels are between 1 and 100, unless not enough data
                # was available; then the avg stress level is reported as -1.
                # We drop these.
                average_stress_level = summary.get('averageStressLevel') if \
                    summary.get('averageStressLevel') is not None and \
                        summary.get('averageStressLevel') > 0 else None,
                max_stress_level = summary.get('maxStressLevel'),
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
            
            update_db_from_api_response(session, daily)
            if summary.get('timeOffsetHeartRateSamples') != {}:
                upsert_time_value_map(current_app.config['ENGINE'], summary.get('timeOffsetHeartRateSamples'),
                    daily.start_time_local, daily.sid, heart_rate_sample.Heart_Rate_Sample)

    return Response(status=200)

@bp.route('/activities', methods=['POST'])
def recieve_activities():
    #NOTE: This is not (at this time) storing parent/child activity data, becuase
    # I can't find any documentation on this except that it may exist. See the
    # Garmin Wellness Activity_Summary data model for more details.
    activities = request.get_json()['activities']
    with current_app.session_scope() as session:
        for summary in activities:
            activity_summary = activity.Activity_Summary(
                sid = uid2sid(session,summary.get('userId')),

                start_time_local = datetime.fromtimestamp(summary.get('startTimeInSeconds') +
                         summary.get('startTimeOffsetInSeconds')),

                duration = to_interval(summary.get('durationInSeconds')),
                
                avg_bike_cadence_rounds_per_minute = summary.get(
                            'averageBikeCadenceInRoundsPerMinute'),
                max_bike_cadence_rounds_per_minute = summary.get(
                            'maxBikeCadenceInRoundsPerMinute'),
                
                avg_heart_rate = summary.get('averageHeartRateInBeatsPerMinute'),
                max_heart_rate = summary.get('maxHeartRateInBeatsPerMinute'),
            
                avg_run_cadence_steps_per_minute = summary.get(
                        'averageRunCadenceInStepsPerMinute'),
                max_run_cadence_steps_per_minute = summary.get(
                        'maxRunCadenceInStepsPerMinute'),

                avg_speed_meters_per_second = summary.get('averageSpeedInMetersPerSecond'),
                max_speed_meters_per_second = summary.get('maxSpeedInMetersPerSecond'),

                avg_swim_cadence_strokes_per_minute = summary.get(
                        'averageSwimCadenceInStrokesPerMinute'),

                avg_pace_minutes_per_km = summary.get('averagePaceInMinutesPerKilometer'),
                max_pace_minutes_per_km = summary.get('maxPaceInMinutesPerKilometer'),
            
                active_kcal = summary.get('activeKilocalories'),
                
                device_name = summary.get('deviceName'),
        
                steps = summary.get('steps'),
                
                distance_meters = summary.get('distanceInMeters'),
        
                number_of_active_lengths = summary.get('numberOfActiveLengths'),
                
                # Probably need IRB approval before we start tracking location
                #starting_latitude_degrees = summary.get('startingLatitudeInDegree'),
                #starting_longitude_degrees = summary.get('startingLongitudeInDegree'),
                
                elevation_gain_total_meters = summary.get('totalElevationGainInMeters'), 
                elevation_loss_total_meters = summary.get('totalElevationLossInMeter'),

                #is_parent = ???
                #parent_summary_id = ???
                
                manually_entered = summary.get('manual'))
            update_db_from_api_response(session, activity_summary)
            
    return Response(status = 200)

@bp.route('/epochs', methods=['POST'])
def recieve_epochs():
    epochs = request.get_json()['epochs']
    with current_app.session_scope() as session:
        for summary in epochs:
            epoch_summary = epoch.Epoch_Summary(
                sid = uid2sid(session,summary.get('userId')),

                start_time_local = datetime.fromtimestamp(summary.get('startTimeInSeconds') +
                         summary.get('startTimeOffsetInSeconds')),

                duration = to_interval(summary.get('durationInSeconds')),
                active_time = to_interval(summary.get('activeTimeInSeconds')),
    
                activity_type = summary.get('activityType'),

                steps = summary.get('steps'),
                
                distance_meters = summary.get('distanceInMeters'),
        
                active_kcal = summary.get('activeKilocalories'),

                metabolic_equivalent_of_task = summary.get('met'),
    
                intensity_qualifer = summary.get('intensity'),

                mean_motion_intensity_score = summary.get('meanMotionIntensity'),
                max_motion_intensity_score= summary.get('maxMotionIntensity'))

            update_db_from_api_response(session, epoch_summary)
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
    with current_app.session_scope() as session:
        for summary in sleeps:
            sleep_summary = sleep.Sleep_Summary(
                sid = uid2sid(session,summary.get('userId')),
                
                start_time_local = datetime.fromtimestamp(summary.get(
                    'startTimeInSeconds') + \
                    summary.get('startTimeOffsetInSeconds')),
                
                duration = to_interval(summary.get('durationInSeconds')),
                unmeasurable_sleep_time = to_interval(summary.get(
                    'unmeasureableSleepInSeconds')),
                validation = summary.get('validation'),
            )                

            # Determine if there is already a sleep record for this subject/time.
            db_sleep = session.query(sleep.Sleep_Summary).filter_by(
                sid=sleep_summary.sid,
                start_time_local = sleep_summary.start_time_local).one_or_none()
            # Copy it over if so
            if db_sleep is not None:
                sleep_summary.id = db_sleep.id
                # Delete the summary and samples associated with the id.
                session.query(sleep_levels_sample.Sleep_Levels_Sample).filter_by(
                    id=sleep_summary.id).delete()
                session.delete(db_sleep)
                session.commit()

            update_db_from_api_response(session, sleep_summary)

            # After we've added our sleep summary, it should have an ID;
            # either auto-generated after adding, or taken from db_sleep.id  
            session.commit()
           
            # sleepLevelsMap come in as dicts with keys denoting a sleep level 
            # qualifier, and values containing dicts with a start time and
            # end time.
            for qualifier in summary.get('sleepLevelsMap'):
                for sample in summary.get('sleepLevelsMap')[qualifier]:
                    sleep_sample = sleep_levels_sample.Sleep_Levels_Sample(
                        id = sleep_summary.id,
                        sleep_qualifier = qualifier,
                        start_time_local = datetime.fromtimestamp(
                            sample['startTimeInSeconds'] + 
                            summary.get('startTimeOffsetInSeconds')),
                        duration = to_interval(sample['endTimeInSeconds'] - 
                            sample['startTimeInSeconds']))
                    session.add(sleep_sample)

    return Response(status = 200)

@bp.route('/bodyComps', methods=['POST'])
def recieve_body_comp():
    body_comps = request.get_json()['bodyComps']
    with current_app.session_scope() as session:
        for summary in body_comps:
            bc = body_comp.Body_Composition(
                sid = uid2sid(session,summary.get('userId')),

                measurement_time_local = datetime.fromtimestamp(
                    summary.get('measurementTimeInSeconds') + summary.get(
                        'measurementTimeOffsetInSeconds')),

                muscle_mass_grams = summary.get('muscleMassInGrams'),
                bone_mass_grams = summary.get('boneMassInGrams'),
            
                body_water_percentage = summary.get('bodyWaterInPercent'),
                body_fat_percentage = summary.get('bodyFatInPercent'),
                body_mass_index = summary.get('bodyMassIndex'),

                weight_grams = summary.get('weightInGrams')
            )
            
            update_db_from_api_response(session,  bc)

    return Response(status = 200)

@bp.route('/stressDetails', methods=['POST'])
def recieve_stress_details():
    stress_details = request.get_json()['stressDetails']
    with current_app.session_scope() as session:
        for summary in stress_details:
                sid = uid2sid(session,summary.get('userId'))
                start_time_local = datetime.fromtimestamp(summary.get('startTimeInSeconds')
                    +summary.get('startTimeOffsetInSeconds'))

                sample_map = summary.get('timeOffsetStressLevelValues')
                if sample_map is not None:
                    # The stress level values are reported as -1 if there
                    # was not enough data to calculate a dress. We want to 
                    # drop these.
                    sample_map = {time:value for time, value in \
                        sample_map.items() if value >= 0}

                    # Make sure there are samples actually left:
                    if sample_map != {}:
                        upsert_time_value_map(
                            current_app.config['ENGINE'], 
                            sample_map,
                            start_time_local, 
                            sid, 
                            stress_sample.Stress_Sample)

                if summary.get('timeOffsetBodyBatteryValues') is not None:
                    upsert_time_value_map(
                        current_app.config['ENGINE'],
                        summary.get('timeOffsetBodyBatteryValues'),
                        start_time_local,
                        sid,
                        body_battery_sample.Body_Battery_Sample)
                

    return Response(status = 200)


@bp.route('/userMetrics', methods=['POST'])
def recieve_user_metrics():
    user_metrics_summaries = request.get_json()['userMetrics']
    with current_app.session_scope() as session:
        for summary in user_metrics_summaries:
            metric_summary = user_metrics.User_Metrics(
                sid = uid2sid(session,summary.get('userId')),
        
                calendar_date = get_calendar_date(summary),
        
                vo2_max_ml_per_min_per_kg = summary.get('vo2Max'),
                fitness_age = summary.get('fitnessAge')
            )
            
            update_db_from_api_response(session, metric_summary)

    return Response(status = 200)

@bp.route('/moveiq', methods=['POST'])
def recieve_moveiq():

    move_iq_summaries = request.get_json()['moveIQActivities']
    with current_app.session_scope() as session:
        for summary in move_iq_summaries:
            move_iq_summary = move_iq.Move_Iq(
                sid = uid2sid(session,summary.get('userId')),

                start_time_local = datetime.fromtimestamp(summary.get('startTimeInSeconds') + 
                    summary.get('offsetInSeconds')),
                duration = to_interval(summary.get('durationInSeconds')),
    
                activity_type = summary.get('activityType'),
                activity_subtype = summary.get('activitySubType')
            )
            update_db_from_api_response(session, move_iq_summary)
                
    return Response(status = 200)

@bp.route('/pulseOx', methods=['POST'])
def recieve_pulseox():
    pulse_ox_summaries = request.get_json()['pulseox']

    with open('pulseox.json.dump','w') as f:
        json.dump(pulse_ox_summaries, f)


    with current_app.session_scope() as session:
        for summary in pulse_ox_summaries:
            sid = uid2sid(session,summary.get('userId'))
            
            start_time_local = datetime.fromtimestamp(summary.get('startTimeInSeconds') +
                summary.get('startTimeOffsetInSeconds'))
            
            if summary.get('timeOffsetSpo2Values') is not None:
                upsert_time_value_map(
                    current_app.config['ENGINE'],
                    summary.get('timeOffsetSpo2Values'),
                    start_time_local,
                    sid,
                    pulse_ox_sample.Pulse_Ox_Sample)
    
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
                                incoming_data):
    """[Parameters:]

        * session: Uses the session that is passed in (so another does
            not need to be created.)
        * incoming_data: the row object of the data we want to insert.
 
    [Background:] 

    When a JSON response is recieved from the garmin wellness API, it may
    include data that is already present in the database in some form. This 
    helper function will pull out any existing data in the database, delete it,
    and enter the new summary.`
    
    In particular, section 6.1 of the Wellness REST API Specification states:

        "The Health API provides updates to previously issued summary records. 
        Updates are summary data records for a given user with the same start  
        time and summary type as a previous summary data record and a duration
        that is either equal to or greater than the previous summary data’s
        duration. [...] Each sync may generate updates and the latest summary
        should always take precedence over previous records."

    This function does not add timeseries data. That is handled separately.
    """
    

    #Pack primary keys into a dictionary to be unpacked as kwargs
    pk_dict = {}
    for pk in inspect(incoming_data).class_.__mapper__.primary_key:
        pk_dict[pk.name] = getattr(incoming_data,pk.name)
    
    #Since the ID's are auto incremented, they aren't generated until an
    #object is added to the database. We remove them from pk_dict here
    #so that they don't cause an issue with filtering our query.
    #TODO: see if you need to uncomment this pk_dict.pop('id', None)    

    #Grab class object
    class_obj = inspect(incoming_data).class_.__mapper__ 

    #Grab the existing data
    db_data = session.query(class_obj).filter_by(**pk_dict).one_or_none()
            
    if db_data is not None:
        session.delete(db_data)
        session.commit()

    session.add(incoming_data)      

    
def uid2sid(session, uid):
    """Convert user identifier to subject identifier using an existing
    session."""
    subject = session.query(Subject).filter_by(garmin_uid=uid).one_or_none()
    if (subject == None):
        return None
    return subject.subject_id


def upsert_time_value_map(engine, to_map, start_time_local, sid, table):
    """Helper function to update timeseries-esque data such as
        * pulse ox samples
        * heart rate samples
        * body batter samples
        * stress samples

    Takes an engine (to open a connection), 
    a time_offset/value mapping, start_time_local, a subject ID,
    and the table to insert into."""
    
    samples = []
    for to_sample in to_map:
        samples.append({
            'time_local' : start_time_local + to_interval(int(to_sample)),
            'value' :  to_map[to_sample],
            'sid' : sid})

    conn = engine.connect()        
    stmt = insert(table).values(samples)
    stmt = stmt.on_conflict_do_nothing(index_elements=['sid','time_local'])
    conn.execute(stmt)

    conn.close()
    
