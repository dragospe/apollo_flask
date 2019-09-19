"""This blueprint recieves data from the Garmin Wellness API push service."""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

from apollo_flask.db import session_scope
from apollo_flask.db.models.garmin_wellness import *

from datetime import date, datetime
import dateutil.parser

bp = Blueprint('garmi_api_client', __name__, url_prefix='/api_client/garmin')

@bp.route('/dailies', methods=['POST'])
def recieve_dailies():
    dailies = request.get_json()['dailies']
    dailies_list = []
    with session_scope() as session:
        for summary in dailies:
            #If a summary in the database with the same summary ID exists, fetch it.
            #We need to update it instead of adding a new one.
            db_daily = session.query(
                daily_summary.Daily_Summary).filter_by(
                    summary_id = summary['summaryId']).first()

            daily = daily_summary.Daily_Summary(
                user_id = summary.get('userId'),
                summary_id = summary.get('summaryId'),
                calendar_date = dateutil.parser.parse(
                    summary.get('calendarDate')).date() if 
                    summary.get('calendarDate') is not None else None,
                start_time = datetime.fromtimestamp(summary.get('startTimeInSeconds')),
                start_time_offset = to_interval(summary.get('startTimeOffsetInSeconds')),
                duration = summary.get('durationInSeconds'),
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

            if db_daily is not None and db_daily.duration <= daily.duration:
                #The summary already existed, but needs to be updated. 
                session.add(db_daily)
                clone_row(daily, db_daily)
            elif db_daily is not None and db_daily.duration > daily.duration:
                #The summary already existed, but does not need to be updated
                pass
            else:
                #The summary did not exist; add it
                session.add(daily)
            #Commit, so that the data is persistant for the next loop.
            session.commit

    return Response(status=200)

@bp.route('/activities', methods=['POST'])
def recieve_activities():
    pass

@bp.route('/mua', methods=['POST'])
def recieve_mua():
    pass

@bp.route('/epochs', methods=['POST'])
def recieve_epochs():
    pass

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
        return str(x) + 's'

def clone_row(from_row, to_row):
    """Helper function to clone mapped objects IN PLACE. This helps we when take 
    the result of a query, and want to update it to match newer data."""
    
    for k in from_row.__table__.columns.keys():
        to_row.__dict__[k] = from_row.__dict__[k]
    
    return to_row
