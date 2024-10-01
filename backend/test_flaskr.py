import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv('DB_TEST_NAME')
        self.database_path = "postgresql://{}/{}".format(
            os.getenv('DB_PATH'), self.database_name)
        setup_db(self.app, self.database_path)

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

    def test_get_questions_success(self):
        response = self.client().get('/questions?page=1')
        data_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)

    def test_get_questions_failed(self):
        response = self.client().get('/questions?page=1000')
        data_json = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data_json['success'], False)
        self.assertEqual(data_json['message'], 'Page not found')

    def test_create_question_success(self):
        new_question = {
            'question': 'What is the capital of VietNam?',
            'answer': 'Ha Noi',
            'difficulty': 2,
            'category': 3
        }
        response = self.client().post('/questions', json=new_question)
        data_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)
        self.assertEqual(
            data_json['message'], 'Question has been added successfully!')

    def test_create_question_invalid(self):
        invalid_question = {
            'question': 'What is the capital of France?',
            'difficulty': 2,
            'category': 3
        }
        response = self.client().post('/questions', json=invalid_question)
        data_json = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data_json['success'], False)
        self.assertEqual(data_json['message'], 'Invalid Request!')

    def test_delete_question_seccess(self):
        # Change number 6 to a valid id for this test case to pass
        response = self.client().delete('/questions/6')
        data_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)
        self.assertEqual(data_json['message'],
                         'The question has been successfully deleted!')

    def test_delete_question_but_not_found_id(self):
        # Change number 5555 to a invalid id for this test case to pass
        response = self.client().delete('/questions/5555')
        data_json = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data_json['success'], False)
        self.assertEqual(data_json['message'], 'Page Not found!')

    def test_get_categories_success(self):
        response = self.client().get('/categories')
        data_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)

    def test_get_categories_fail(self):
        response = self.client().delete('/categories')
        data_json = json.loads(response.data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data_json["success"], False)
        self.assertEqual(data_json['message'], 'Request not allowed')

    def test_get_questions_base_on_category_not_found_id(self):
        # Change number 200 to a invalid id for this test case to pass
        response = self.client().get('/categories/200/questions')
        data_json = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data_json['success'], False)
        self.assertEqual(data_json['message'], 'Page Not found!')

    def test_get_questions_base_on_category_success(self):
        # Change number 1 to a valid id for this test case to pass
        response = self.client().get('/categories/1/questions')
        data_json = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)

    def test_search_questions(self):
        # send post request with search term
        response = self.client().post(
            '/questions', json={'searchTerm': 'Washington'})
        data_json = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)
        self.assertEqual(len(data_json['questions']), 1)
        self.assertEqual(data_json['questions'][0]['id'], 23)

    def test_404_if_search_questions_fails(self):
        response = self.client().post(
            '/questions', json={'searchTerm': 'abcdefghijk'})
        data_json = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data_json['success'], False)
        self.assertEqual(data_json['message'], 'Question not found!')

    def test_quiz_game(self):
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [20, 21], 'quiz_category': {'type': 'Science', 'id': '1'}})
        data_json = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_json['success'], True)
        self.assertTrue(data_json['question'])
        self.assertEqual(data_json['question']['category'], 1)
        self.assertNotEqual(data_json['question']['id'], 20)
        self.assertNotEqual(data_json['question']['id'], 21)

    def test_quiz_fail(self):
        response = self.client().post('/quizzes', json={})
        data_json = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data_json['success'], False)
        self.assertEqual(data_json['message'], 'Bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
