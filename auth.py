from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.db_helpers import *
from flask_login import current_user, login_user, logout_user
from app.user import User
from app.forms import RegistrationForm, PanelistDetailsForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Endpoint for creating a username and password to log in.

    On GET request:
        Email field is pre-populated with the session data from the landing
        page's email input form.  If they enter it there then there is no
        reason to enter it again.
    
    On POST request:
        email, password, and confirm_password fields are validated and then
        a query checks to see if there is already a Panelist registered with 
        that given email.  If there is, an error is flashed saying so.  If
        there is not, then the email and the hashed password are inserted and
        commited into the Panelists table.
        """
    # TODO: The panelist's email is entered into the session, and then this
    # is used in the update query to define which panelist row to update.  I
    # believe this will be better handled by calling lastrowid method/attribute
    # of cursor object 'DB' there. Probably not great to use session data.
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        db = get_db()
        error = None
        if db.execute('SELECT panelist_id FROM Panelists WHERE email = ?', (email,)).fetchone() is not None:
            error = 'User {} is already registered.'.format(email)
        else:
            db.execute('INSERT INTO Panelists (email, password) VALUES (?, ?)', (email, generate_password_hash(password)))
            db.commit()
            session.clear()
            session['email'] = email
            return redirect(url_for('auth.details'))
        flash(error)
    
    form.email.data = session['email']
    return render_template('auth/register.html', form=form)


@bp.route('/details/', methods=('GET', 'POST'))
def details():
    """Endpoint for inputting demographic information after registration.

    Currently this is accessible by URL but ideally it is locked for access
    solely after succesfully registering with email and password.

    On GET request:
        Display HTML template with the PanelistDetailsForm.

    On POST Request:
        Validate the form inputs and update the Panelist row with the given
        information.
        Query the Panelist table to get the full row for the panelist and log
        them in by creating a User object with their panelist row and then
        passing that User object to the login_user method of flask-login.
        """

    # TODO: Use the lastrowid method/attribute of the db cursor object as the
    # way to designate the panelist_id to update.

    form = PanelistDetailsForm(request.form)
    if request.method == 'POST' and form.validate():
        firstname = form.firstname.data
        lastname = form.lastname.data
        dob = form.dob.data
        race = form.race.data
        gender = form.gender.data
        region = form.region.data
        panelist_to_update = session['email']
        
        db = get_db()
        db.execute('UPDATE Panelists SET firstname = ?, lastname = ?, dob = ?, race = ?, gender = ?, region = ? WHERE email = ?',
                    (firstname, lastname, dob, race, gender, region, panelist_to_update))
        db.commit()

        panelist_to_login = db.execute('SELECT * FROM Panelists WHERE email = ?', (panelist_to_update,)).fetchone()
        
        login_user(User(panelist_to_login))
        return redirect(url_for('views.home'))
            
    return render_template('auth/details.html', form=form)


@bp.route('/login/', methods=(['GET', 'POST']))
def login():
    """Endpoint for logging in a user based on their provided email and password.

    On GET request:
        Display HTML template with PanelistLoginForm.

    On POST request:
        1. Validate email and password fields.
        2. Query Panelists for that email and if no such row exists or the
           hashed password does not match the stored info, then flash error.
        3. Otherwise create a User object with that query and pass to 
           login_user().  Then redirect to the home page.
    """

    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        db = get_db()
        error = None
        panelist_to_login = db.execute('SELECT * FROM Panelists WHERE email = ?', (username,)).fetchone()

        if panelist_to_login is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(panelist_to_login['password'], password):
            error = 'Incorrect username or password.'
        elif error is None:
            session.clear()
            login_user(User(panelist_to_login))
            return redirect(url_for('views.home'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout/')
def logout():
    """This will always be a GET request to clear session, logout_user(), and
    redirect to the landing page"""

    session.clear()
    logout_user()
    return redirect(url_for('views.index'))