from flask import Blueprint, flash, render_template
from flask_login import current_user
from app.db_helpers import *
from app.decorators import login_required

bp = Blueprint('answer', __name__, url_prefix='/answer')


@bp.route('/<string:sort_parameter>/', methods=(['GET', 'POST']))
@login_required
def browse(sort_parameter):
    """Endpoint for displaying surveys to browse and click on to begin taking.

    sort_parameter determines which query to use in displaying Surveys to the HTML page.
    """

    db = get_db()

    if sort_parameter == 'recommended':
        surveys = getEligibleSurveys(current_user).fetchall()
    elif sort_parameter == 'shortest':
        surveys = query('SELECT * FROM Surveys ORDER BY completion_time ASC').fetchall()
    elif sort_parameter == 'longest':
        surveys = query('SELECT * FROM Surveys ORDER BY completion_time DESC').fetchall()
    elif sort_parameter == 'newest':
        surveys = query('SELECT * FROM Surveys ORDER BY create_date DESC').fetchall()
    elif sort_parameter == 'oldest':
        surveys = query('SELECT * FROM Surveys ORDER BY create_date ASC').fetchall()
    elif sort_parameter == 'all':
        surveys = query('SELECT * FROM Surveys').fetchall()

            
    return render_template('answer/browse.html', surveys=surveys)


@bp.route('/<int:survey_id>', methods=(['GET', 'POST']))
@login_required
def answer(survey_id):
    """Endpoint for answering a survey with a given survey_id.

    Arguments:
    survey_id: the survey_id of the survey to be displayed.

    Creates variable survey_info with a query of the Surveys table to pass
    to HTML template the survey's title, length, completion_time, etc.
    """

    db = get_db()
    survey_info = getSurveyDetails(survey_id)
    questions = getSurveyQuestions(survey_id)
    question_dictionary = createSurveyDictionary(questions)

    return render_template('answer/answer.html', survey_info=survey_info, questions=questions, question_dictionary=question_dictionary)


@bp.route('/questionbank/', methods=['GET', 'POST'])
@login_required
def questionbank():
    """Endpoint for displaying all questions from every survey at once.

    Undecided about incorporating this at this point.  While it is another
    display of SQL skills, it seems to undermine the individual survey
    functionality and product vision that this site promotes.  Plus it would
    likely need some sort of pagination that I am not familiar with at this
    point and would like to work on other areas of the program before doing 
    this.
    """

    db=get_db()
    questions = db.execute('SELECT * FROM questions').fetchall()
    question_dictionary = createSurveyDictionaryBank(questions)

    return render_template('answer/questionbank.html', questions=questions, question_dictionary=question_dictionary)