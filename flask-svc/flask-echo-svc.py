from flask import Flask
from flask import request
import os


application = Flask(__name__)


@application.route("/")
def hello():
    return "%s: Hello World! [Remote_addr]%s [X-Forwarded-For]%s\n" % (os.popen('ip netns identify').read().strip(), request.remote_addr, request.headers.get('X-Forwarded-For')), 200



if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
