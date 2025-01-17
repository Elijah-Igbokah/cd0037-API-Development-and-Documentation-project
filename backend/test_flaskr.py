import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
# from backend.settings import DB_NAME_TEST

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME_TEST, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME_TEST
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            DB_USER, DB_PASSWORD, "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Who is the biggest man on Mars?",
                             "answer": "Mr Nobody", "category": "2", "difficulty": "5"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_question_by_category(self):
        res = self.client().get('/categories/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_404_get_question_beyond_valid_categories(self):
        res = self.client().get('/categories/69')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_page(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=3000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_delete_question(self):
        """ 
        Tests question delete success
        """
        # First create a new question to be deleted
        question = Question(question="What does the fox say?",
                            answer='Moo', category=1, difficulty=1)
        question.insert()
        question_id = question.id

        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    def test_422_delete_request_not_processed(self):
        res = self.client().delete('/questions/3000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'error in processing request')

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['answer'])
        self.assertTrue(data['difficulty'])

    def test_422_if_question_creation_not_valid(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'error in processing request')

    def test_search_questions(self):
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_404_get_search_unavailable_question(self):
        res = self.client().post('/questions/search',
                                 json={"searchTerm": "bjsjcbsbsabj"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
