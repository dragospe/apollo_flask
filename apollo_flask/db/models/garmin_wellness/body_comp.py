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

    measurement_time_local = Column(DateTime,
        CheckConstraint("measurement_time_local >= date '2019-01-01'", 
            name = 'measurement_time >= 2019'),
        primary_key = True) 

    muscle_mass_grams = Column(Integer, 
        CheckConstraint("muscle_mass_grams >= 0", name ="muscle_mass >= 0"))
    bone_mass_grams = Column(Integer, CheckConstraint("bone_mass_grams >= 0",
        name = "bone_mass_grams >= 0"))
    
    body_water_percentage = Column(Float, CheckConstraint(
        "body_water_percentage >= 0 AND body_water_percentage <= 100",
        name= "body_water bounds"))
    body_fat_percentage = Column(Float, CheckConstraint(
        "body_fat_percentage >= 0 AND body_fat_percentage <= 100",
        name = "body_fat_bounds"))
    body_mass_index = Column(Float, CheckConstraint(
        "body_mass_index >= 0", name = "bmi >= 0"))
    
    weight_grams = Column(Integer, CheckConstraint("weight_grams >= 0", 
        name = "weight_grams >= 0"))
