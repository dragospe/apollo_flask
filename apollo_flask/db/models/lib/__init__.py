#Package imports (to minimize the imports needed for each file in 'models')
import sqlalchemy
from sqlalchemy import (Column, Integer, Float, String, Enum, DateTime, Date,
    ForeignKey, CheckConstraint, Boolean, UniqueConstraint)

from sqlalchemy.dialects.postgresql import INTERVAL, JSON

from sqlalchemy.types import JSON

from sqlalchemy.exc import ProgrammingError

from sqlalchemy.orm import relationship

from apollo_flask.db import Base

#The activity types defined by the wellness API in appendix A
ACTIVITY_TYPE_ENUM =  Enum('UNCATEGORIZED',
	'SEDENTARY',
	'SLEEP',
	'RUNNING',
	'STREET_RUNNING',
	'TRACK_RUNNING',
	'TRAIL_RUNNING',
	'TREADMILL_RUNNING',
	'CYCLING',
	'CYCLOCROSS',
	'DOWNHILL_BIKING',
	'INDOOR_CYCLING',
	'MOUNTAIN_BIKING',
	'RECUMBENT_CYCLING',
	'ROAD_BIKING',
	'TRACK_CYCLING',
	'FITNESS_EQUIPMENT',
	'ELLIPTICAL',
	'INDOOR_CARDIO',
	'INDOOR_ROWING',
	'STAIR_CLIMBING',
	'STRENGTH_TRAINING',
	'HIKING',
	'SWIMMING',
	'LAP_SWIMMING',
	'OPEN_WATER_SWIMMING',
	'WALKING',
	'CASUAL_WALKING',
	'SPEED_WALKING',
	'TRANSITION',
	'SWIMTOBIKETRANSITION',
	'BIKETORUNTRANSITION',
	'RUNTOBIKETRANSITION',
	'MOTORCYCLING',
	'OTHER',
	'BACKCOUNTRY_SKIING_SNOWBOARDING',
	'BOATING',
	'CROSS_COUNTRY_SKIING',
	'DRIVING_GENERAL',
	'FLYING',
	'GOLF',
	'HORSEBACK_RIDING',
	'INLINE_SKATING',
	'MOUNTAINEERING',
	'PADDLING',
	'RESORT_SKIING_SNOWBOARDING',
	'ROWING',
	'SAILING',
	'SKATE_SKIING',
	'SKATING',
	'SNOWMOBILING',
	'SNOW_SHOE',
	'STAND_UP_PADDLEBOARDING',
	'WHITEWATER_RAFTING_KAYAKING',
	'WIND_KITE_SURFING', 
        name='Activity_Type',
        schema='garmin_wellness')

STRESS_QUALIFIER_ENUM = Enum( 'unknown', 'calm', 'balanced', 'stressful',
    'very_stressful', 'calm_awake', 'balanced_awake', 'stressful_awake',
    'very_stressful_awake', name="Stress_Qualifier", schema = 'garmin_wellness')

#From appendix B of the API specification
WELLNESS_MONITORING_INTENSITY_ENUM = Enum('SEDENTARY', 'ACTIVE',
    'HIGHLY_ACTIVE', name='Wellness_Monitoring_Intensity', 
    schema= 'garmin_wellness')

#From section 7.8 of the API specification
SLEEP_VALIDATION_ENUM = Enum('MANUAL', 'DEVICE', 'AUTO_TENTATIVE', 'AUTO_FINAL', 'AUTO_MANUAL', 'ENHANCED_TENTATIVE', 'ENHANCED_FINAL', name='Sleep_Validation', schema = 'garmin_wellness')
