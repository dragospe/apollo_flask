from apollo_flask.db.models.lib import *
import apollo_flask.db.models

class Body_Composition(Base):
    """Stores body composition data for users.
    All masses given in grams. 
    All times given in seconds.
    Percentages given as floats in [0.0 - 100.0]"""

    __tablename__ = 'body_composition'
    __table_args__ = {'schema':'garmin_wellness'}

    sid = Column(String, ForeignKey('subject.subject_id'),
         primary_key = True)

    measurement_time_utc = Column(DateTime, primary_key = True) 
    measurement_time_offset = Column(INTERVAL)

    muscle_mass = Column(Integer)
    bone_mass = Column(Integer)
    
    body_water_percentage = Column(Float)
    body_fat_percentage = Column(Float)
    body_mass_index = Column(Float)
    
    weight = Column(Integer)
