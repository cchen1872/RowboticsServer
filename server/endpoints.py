"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from flask import Flask, request, Response
from flask_restx import Resource, Api, fields
from flask_cors import CORS
from http.client import (
    OK,
    CONFLICT,
    UNAUTHORIZED,
    NO_CONTENT,
    BAD_REQUEST
)
from os import getpid, kill
from signal import SIGTERM
from data.MessageAnnouncer import MessageAnnouncer
from data.sse import format_sse
from threading import Thread, Lock
import data.users as users
import time

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*', "access-control-allow-origin": "*"}})
api = Api(app)

announcer = MessageAnnouncer()
listening_probe = False
mutex = Lock()

@api.route('/listen/<username>')
class Listener(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self, username) -> dict:
        global listening_probe
        def stream():
            # global listening_probe
            messages = announcer.listen(username)  # returns a queue.Queue
            while listening_probe:
                msg = messages.get()  # blocks until a new message arrives
                yield msg
            return None
        
        listening_probe = True
        return Response(stream(), mimetype='text/event-stream')

@api.route('/test')
class Tester(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self) -> dict:
        return "TESTING"


@api.route('/open')
class OpenStream(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def patch(self):
        global listening_probe
        if listening_probe:
            msg = format_sse(data='opening', event='open')
            announcer.announce(msg=msg)


@api.route('/close')
class CloseStream(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def patch(self):
        global listening_probe
        if listening_probe:
            listening_probe = False
            msg = format_sse(data='finished', event='close')
            announcer.announce(msg=msg)
            announcer.close()
        


@api.route('/ping')
class Ping(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def patch(self):
        global listening_probe
        if listening_probe:
            t_obj = time.time()
            msg = format_sse(data=t_obj)
            announcer.announce(msg=msg)
            return {}, 200
        else:
            return {}, 409


@api.route('/users')
class Users(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        users.getusers()
