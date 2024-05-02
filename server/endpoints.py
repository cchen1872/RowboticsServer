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
from data.sse import format_sse
import data.users as users
import time
from threading import Thread
from data.MessageAnnouncer import MessageAnnouncer
from data.sensors.read_sensors import ReadSensors

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*', "access-control-allow-origin": "*"}})
api = Api(app)


listening_probe = False
announcer = MessageAnnouncer()

@api.route('/listen')
class Listener(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self) -> dict:
        global listening_probe
        global announcer
        # def stream(thread):
        def stream(thread):
            global announcer
            # global listening_probe
            announcer.listen()  # returns a queue.Queue
            # print(f'{listening_probe=}')
            # print(f'{announcer.listener=}')
            while listening_probe:
                msg = announcer.get()  # blocks until a new message arrives
                yield msg
            thread.join()
            return None
        
        if announcer.isOpen():
            return None
        listening_probe = True
        print("SDFJKJFSKL")
        print(f'{listening_probe=}')
        thread = Thread(target=ReadSensors, args=("SensorThread", announcer))
        thread.daemon = True
        thread.start()
        return Response(stream(thread), mimetype='text/event-stream')
        # return Response(stream(), mimetype='text/event-stream')

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
        global announcer
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
        global announcer
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
        global announcer
        print(listening_probe)
        if listening_probe:
            t_obj = time.time()
            msg = format_sse(data=t_obj, event='message')
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
