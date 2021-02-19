from app.db_helpers import *
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from app.db import get_db
from flask_login import current_user
from app.decorators import login_required
from app.forms import MultiCheckboxField, SurveyDetailsForm
bp = Blueprint('create', __name__, url_prefix='/ask')


@bp.route('/', methods=(['GET', 'POST']))
@login_required
def create_index():
    """Endpoint for creating a survey based on its basic information.

    On GET request:
        Display HTML template with SurveyDetailsForm.
    
    On POST request:
        1. Validate form fields and insert all but races, genders, and regions
           into Surveys table.
        2. Get the survey_id of the newly added survey.
        3. Insert the elements in the genders list into survey_genders using the
           newly created survey_id as the survey_id.
        4. Same for races.
        5. Same for regions.
        6. Redirect to the create_survey HTML template for the survey_id.
    """

    form = SurveyDetailsForm()
    if request.method == 'POST' and form.validate():
        publisher = current_user.panelist_id
        category = form.category.data
        title = form.title.data
        survey_description = form.survey_description.data
        sample_size = form.sample_size.data
        min_age = form.min_age.data
        max_age = form.max_age.data
        genders = form.gender.data
        races = form.race.data
        regions = form.region.data

        # create the new entry in surveys
        db = get_db()
        
        db.execute(
            'INSERT INTO Surveys\
                (publisher, category, title, survey_description, sample_size, min_age, max_age) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (publisher, category, title, survey_description, sample_size, min_age, max_age))
        db.commit()

        # query to get the survey ID of the newly created survey
        db = get_db()
        created_survey_id = db.execute('SELECT survey_id FROM Surveys WHERE publisher = ? ORDER BY create_date DESC',\
                                        (publisher,)).fetchone()
        survey_id = int(created_survey_id['survey_id'])
        
        # make entries into survey_races, survey_genders, survey_regions using the survey_id and list of IDs in genders/races/regions
        db = get_db()
        for gender_id_provided in genders:
            db.execute('INSERT INTO survey_genders (survey_id, gender_id) VALUES (?,?)', (survey_id, int(gender_id_provided)))
        db.commit()

        db = get_db()
        for race_id_provided in races:
            db.execute('INSERT INTO survey_races (survey_id, race_id) VALUES (?,?)', (survey_id, int(race_id_provided)))
        db.commit()

        db = get_db()
        for region_id_provided in regions:
            db.execute('INSERT INTO survey_regions (survey_id, region_id) VALUES (?,?)', (survey_id, int(region_id_provided)))
        db.commit()

        return redirect(url_for('create.create_survey', survey_id=survey_id))

    return render_template('ask/create_index.html', form=form)


@bp.route('/<int:survey_id>', methods=(['GET', 'POST']))
@login_required
def create_survey(survey_id):
    """Endpoint to add questions to a given survey.

    On GET request:
        1. getSurveyDetails retrieves the Surveys row of the given survey_id.
        2. getSurveyQuestions retrieves the Question rows for the survey_id.
        3. createSurveyDictionary creates a dictionary using the questions
           that allows for accessing a question's answers.  This is helpful
           in displaying the answers for each question in the Jinja code for
           the HTML template.
        4. Pass these 3 variables to the HTML template for Jinja use.
    
    On POST request:
        1. Validate and store requested data in variables.
        2. Insert question_text into Questions table.
        3. Get the question_id of the newly created question.
        4. Insert the answer elements in answers_to_add into Answers with
           that question_id.
        5. Return a redirect to the same page, but now show the new question
           too.
    """

    # TODO: Create a SurveyQuestionForm that has a text area field for the
    # question_text, and then 4 fields for the answers.  If nothing inputted,
    # do not make an entry in the Answers table.

    if request.method == 'POST':
        #if the add question button is pressed, add the current question and the current answers to the session
        question_text = request.form['question']

        q_a1 = request.form['answer1']
        q_a2 = request.form['answer2']
        q_a3 = request.form['answer3']
        q_a4 = request.form['answer4']

        answers_to_add = [q_a1, q_a2, q_a3, q_a4]
        
        db = get_db()
        db.execute(
            'INSERT INTO new_questions (parent_survey, question) VALUES (?, ?)',
            (survey_id, question_text)
        )
        db.commit()
        db = get_db()
        parent_question = db.execute(
            'SELECT question_id FROM new_questions WHERE parent_survey = ? ORDER BY question_id DESC',
            (survey_id,)
        ).fetchone()


        for answer_text in answers_to_add:
            db = get_db()
            db.execute(
                'INSERT INTO new_answers (parent_question, answer) VALUES (?, ?)',
                (parent_question['question_id'], answer_text)
            )
        db.commit()

        return redirect(url_for('create.create_survey', survey_id=survey_id))

    current_survey = getSurveyDetails(survey_id)
    current_questions = getSurveyQuestions(survey_id)
    question_dictionary = createSurveyDictionary(current_questions)

    return render_template('ask/create_survey.html', current_survey=current_survey, current_questions=current_questions, question_dictionary=question_dictionary)