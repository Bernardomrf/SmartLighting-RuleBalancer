import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue
from flask import Flask, Response, render_template, request
import json
import time

class ServerSentEvent(object):
    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: 'data',
            self.event: 'event',
            self.id: 'id'
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ['%s: %s' % (v, k)
                 for k, v in self.desc_map.items() if k]

        return '%s\n\n' % '\n'.join(lines)


app = Flask(__name__)
subscriptions = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/debug')
def debug():
    return 'Currently %d subscriptions' % len(subscriptions)


@app.route('/status', methods=['POST'])
def publish():
    data = request.get_json(force=True)

    #print(data)
    def notify():
        msg = json.dumps(data)
        for sub in subscriptions[:]:
            sub.put(msg)

    gevent.spawn(notify)
    return "OK"


@app.route('/subscribe')
def subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit:
            subscriptions.remove(q)

    return Response(gen(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.debug = True
    server = WSGIServer(('0.0.0.0', 8080), app)
    server.serve_forever()
