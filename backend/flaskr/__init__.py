import os
from sqlalchemy import func
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_categories = {
                str(category.id): category.type for category in categories}

            return jsonify(
                {
                    'success': True,
                    'categories': formatted_categories
                }
            )

        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        try:
            page_number = request.args.get('page', 1, type=int)
            start_page = (page_number - 1) * QUESTIONS_PER_PAGE
            end_page = start_page + QUESTIONS_PER_PAGE

            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]

            categories = Category.query.all()
            formatted_categories = {
                str(category.id): category.type for category in categories}

            return jsonify(
                {
                    'success': True,
                    'questions': formatted_questions[start_page:end_page],
                    'totalQuestions': len(formatted_questions),
                    'categories': formatted_categories,
                    # In this case, I don't know where to get the current Category. So I'm leaving it as None
                    'currentCategory': None
                }
            )

        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if not question:
            abort(404)
        try:
            question.delete()

            return jsonify(
                {
                    'success': True,
                    'message': 'The question has been successfully deleted!'
                }
            )
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        data_json = request.get_json()

        if 'question' not in data_json or 'answer' not in data_json or 'difficulty' not in data_json or 'category' not in data_json:
            abort(400)

        try:
            question = Question(
                question=data_json['question'],
                answer=data_json['answer'],
                difficulty=data_json['difficulty'],
                category=data_json['category']
            )
            question.insert()

            return jsonify(
                {
                    'success': True,
                    'message': 'Question has been added successfully!'
                }
            )

        except Exception as e:
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            search_term = request.get_json().get('searchTerm')
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify(
                {
                    'success': True,
                    'questions': formatted_questions,
                    'totalQuestions': len(formatted_questions),
                    # In this case, I don't know where to get the current Category. So I'm leaving it as None
                    'currentCategory': None
                }
            )
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        category = Category.query.filter_by(id=category_id).first()
        if category is None:
            abort(404)
        try:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': category.type
            })
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            data_json = request.get_json()
            category = data_json.get('category')
            previous_questions = data_json.get('previous_questions', [])

            query = Question.query.filter(
                Question.id.notin_(previous_questions))
            if category:
                query = query.filter_by(category=category)
            random_question = query.order_by(func.random()).first()

            if random_question:
                formatted_question = random_question.format()
            else:
                formatted_question = None

            return jsonify(
                {
                    'success': True,
                    'question': formatted_question
                }
            )
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def invalid_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Invalid Request!"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page Not found!'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable!'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error!'
        }), 500

    return app
