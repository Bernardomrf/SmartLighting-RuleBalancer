import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
from flask import Flask, Response, render_template, request
import json


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/suggestions')
def suggestions():


    return render_template('suggestions.html', suggestions=suggestions_list)


if __name__ == '__main__':
    app.debug = True
    server = WSGIServer(('0.0.0.0', 8080), app)
    server.serve_forever()
