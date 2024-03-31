"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask, request
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from http.client import (
    OK,
    CONFLICT,
    UNAUTHORIZED,
    NO_CONTENT,
    BAD_REQUEST
)

app = Flask(__name__)
CORS(app)
api = Api(app)

@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self) -> dict:
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {'hello': 'world'}

