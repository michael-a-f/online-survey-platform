import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

from flask_login import current_user, login_user
from app.user import User
from app.db_helpers import *

from app.decorators import login_required

bp = Blueprint('views', __name__)


@bp.route('/home/', methods=(['GET', 'POST']))
@login_required
def home():
    home_surveys = getEligibleSurveys(current_user).fetchmany(size=3)
    db = get_db()
    my_created_surveys = db.execute('SELECT * FROM Surveys WHERE publisher = ?', (current_user.panelist_id,)).fetchall()

    return render_template('views/home.html', home_surveys = home_surveys, my_created_surveys=my_created_surveys)


@bp.route('/', methods=(['GET', 'POST']))
def index():
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('auth.register'))
    
    return render_template('views/index.html')


# This queries the panelists table to get the Guest account, creates a User object with its data, logs that user in, 
# and redirects to the home page
@bp.route('/guest/', methods=(['GET', 'POST']))
def guest():
    session.clear()
    db = get_db()
    guest = db.execute('SELECT * FROM Panelists WHERE panelist_id = 2').fetchone()
    login_user(User(guest))
    return redirect(url_for('views.home'))


@bp.route('/profile/', methods=(['GET', 'POST']))
@login_required
def profile():
    db = get_db()
    my_info = db.execute('SELECT * FROM Panelists WHERE panelist_id = ?', (current_user.panelist_id,)).fetchone()
    my_created_surveys = db.execute('SELECT * FROM Surveys WHERE publisher = ?', (current_user.panelist_id,)).fetchall()
    #my_completed_surveys

    return render_template('views/profile.html', my_info=my_info, my_created_surveys=my_created_surveys)


@bp.route('/redeem/', methods=['GET', 'POST'])
@login_required
def redeem():
    db=get_db()

    return render_template('views/redeem.html')