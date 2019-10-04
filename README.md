[DRAFT]

* Summary endpoints for gamin wellness API are named according to the resource URL from garmin
* the db is organized into schemas based on user authentication (garmin_oauth) and internally/externalled sourced data (garmin_wellness)
* Tests are run with pytest; testing coverage can be checked using 'coverage'.
* the database is set up using sqlalchemy. A library is provided to manage imports for models.

[TIPS]
* When you add a model to the data model, make sure to add it to the __init__.py file to ensure it gets put in the library. Also make sure that you do a backref on the User table, if relevant.


[TODO:]
* The tests right now take a big ball of json, parse it out, add it to the database, and then look for the presence of certain records in the database.
    This mapping from api->db is error prone for at least two reason:
        * Spelling mistakes may occur when converting from garmin's verboseCamelCase to a style_that_we_use.
        * Not every summary returned will have every field, and thus we use the dict's .get method rather than indexing on a key. This means
            that if a key is not present, .get will return None rather than throwing an error; this means that spelling (or other) mistakes
            may not be caught as they usually would.
    The takeaway is that these tests could be improved to ensure that the data from the database matches exactly the data that should have been entered.
    Maybe theres a better way to do this.
* Make the test cases query via User_Id and ensure that the relationships are working
