from app import db
from app.db import get_db
import sqlite3


# Function to shorten query writing process.  Still need to use fetchall/fetchmany/fetchone with the output.
def query(query_string):
    db = get_db()
    res = db.execute(query_string)
    return res


# Take in a query result for selecting the questions that relate to a certain surveyID and returns a dictionary with question_ids as keys and its answers as values.
def createSurveyDictionary(query_result):
    db = get_db()
    question_dictionary = {}
    
    for question_row in query_result:
        question_number = question_row[13]
        answers_rows = db.execute(
            'SELECT a.answer FROM Questions q INNER JOIN Answers a on a.parent_question = q.question_id WHERE q.question_id = ?',
            (question_number,)
            ).fetchall()
        question_dictionary[question_number] = [answer_row[0] for answer_row in answers_rows]

    return(question_dictionary)


def getSurveyDetails(survey_id):
    db = get_db()
    survey_info = db.execute('SELECT * FROM new_surveys WHERE survey_id = ?', (survey_id,)).fetchone()
    return survey_info


def getSurveyQuestions(survey_id):
    db = get_db()
    survey_questions = db.execute(
        'SELECT * FROM new_surveys s INNER JOIN new_questions q on q.parent_survey = s.survey_id WHERE s.survey_id = ?',
        (survey_id,)
    ).fetchall()
    return survey_questions


# Takes in a current_user object and finds all the surveys that this user is eligible for taking.
def getEligibleSurveys(user):
    race = user.race
    gender = user.gender
    region = user.region
    age = user.age

    db = get_db()

    recommended_surveys = db.execute(
            'SELECT *\
            FROM Surveys s\
            INNER JOIN survey_races sr ON sr.survey_id = s.survey_id\
            INNER JOIN Races r on r.race_id = sr.race_id\
            INNER JOIN survey_genders sg ON sg.survey_id = s.survey_id\
            INNER JOIN Genders g on g.gender_id = sg.gender_id\
            INNER JOIN survey_regions se ON se.survey_id = s.survey_id\
            INNER JOIN Regions e on e.region_id = se.region_id\
            WHERE r.race = ?\
            AND g.gender = ?\
            AND e.region = ?\
            AND s.min_age <= ?\
            AND s.max_age >= ?',
            (race, gender, region, age, age)
        )
    
    return recommended_surveys


def getAllRaces():
    db = get_db()
    races_list = db.execute('SELECT race FROM Races')
    return races_list


def getAllGenders():
    db = get_db()
    genders_list = db.execute('SELECT gender FROM Genders')
    return genders_list


def getAllRegions():
    db = get_db()
    regions_list = db.execute('SELECT region FROM Regions')
    return regions_list