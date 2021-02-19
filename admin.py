from app.db_helpers import *
from flask import Blueprint, render_template
from app.decorators import login_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/tables', methods=(['GET']))
@login_required
def admin():
    """Endpoint for displaying tables for Panelists, Surveys,
    and the Juntion tables for survey_races, survey_genders,
    and survey_regions.
    """
    
    panelists = query('SELECT * FROM Panelists').fetchall()
    surveys = query('SELECT * FROM Surveys').fetchall()
    genders = query('SELECT * FROM survey_genders').fetchall()
    races = query('SELECT * FROM survey_races').fetchall()
    regions = query('SELECT * FROM survey_regions').fetchall()

    return render_template('admin/admintables.html', panelists=panelists, surveys=surveys, genders=genders, races=races, regions=regions)