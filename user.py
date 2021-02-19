from . import db
from app.db import get_db
from app import login_manager
from datetime import date


class User(object):
    """Class for a User object to enable Flask-Login's current_user method.

    Arguments:
    This class takes in a Panelist sqlite Row from a query result and
    creates a User object with the data of that panelist.  Because I am not
    using an ORM like SQLAlchemy, I cannot use UserMixin which provides default
    implementations for the properties and methods below.

    Attributes:
    email: the panelist's email.
    name: the panelist's name.
    user_id: the panelist's panelist_id converted to Unicode, as this is needed
             for the function get_user(user_id), per the built-in methods of
             Flask-Login.
    panelist_id: the panelist's panelist_id.
    age: the panelist's age, which is the panelist's dob inputted into
         the function calculate_age(dob).
    race: the panelist's race.
    gender: the panelist's gender.
    region: the panelist's region.
    point_balance: the panelist's point balance.
    """


    def __init__(self, panelist):
        """Initializes the User object using the panelist sqlite row data."""

        self.email = panelist['email']
        self.name = panelist['firstname']
        self.user_id = chr(panelist['panelist_id'])
        self.panelist_id = panelist['panelist_id']
        self.age = calculate_age(panelist['dob'])
        self.race = panelist['race']
        self.gender = panelist['gender']
        self.region = panelist['region']
        self.point_balance = panelist['point_balance']


    def is_guest(self):
        """Always False. Necessary property to make this User class compatible
        with Flask-Login. 
        
        'Guest' functionality is handled by having a designated Panelist row 
        for Guests.
        """

        return False


    def is_authenticated(self):
        """Always True.  This is a necessary property to make this User class
        compatible with Flask-Login.
        """

        return True


    def is_active(self):
        """Always True.  This is a necessary property to make this User class
        compatible with Flask-Login.
        """

        return True


    def is_anonymous(self):
        """Always False.  This is a necessary property to make this User class
        compatible with Flask-Login.
        """

        return False


    def get_id(self):
        """Returns the unicode user_id of the User object. Used by the
        user_loader callback method of Flask-Login login_manager.
        """

        return self.user_id


@login_manager.user_loader
def load_user(user_id):
    """Intakes a unicode user_id and returns a User object for the panelist
    with that id.

    This converts the unicode back to an integer, queries the Panelists table
    for the panelist with that panelist_id, and returns a User object created
    from that panelist's data.
    """

    user_id_integer = ord(user_id)
    db = get_db()
    panelist = db.execute('SELECT * from Panelists WHERE panelist_id = ?', (user_id_integer,)).fetchone()
    return User(panelist)


def calculate_age(born):
    """Returns an Integer for the age of a panelist.

    The panelist DOB column is stored as 'YYYY-MM-DD', so this function
    calculates age as the difference between the current year, and (YYYY) cast
    to an integer.
    """

    today = date.today()
    return today.year - int(born[0:4])