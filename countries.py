
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path as path
from os import environ as environ
import re

appname="countries"
appversion="0.9a"
appauthor="Marco Galanti"
appdescription="This app use RestAPI for performing different functions for testing and demo purpose"
appdisclaimer="DEMO only, not intended for production use"


app = Flask(__name__)
app.secret_key = environ['SECRET_KEY']
basedir = path.abspath(path.dirname(__file__))

#### SQLITE3 DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path.join(basedir, 'countries.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
###############

# POSTGRESQL DB
#SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
#app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

import users_view, addresses_view

from country.views import country
import views

# Blueprint Setup
app.register_blueprint(country, url_prefix="/countries/")

app.config['DEBUG'] = 1

app = Flask(__name__, static_folder="static", template_folder="templates")
def printlog(entry, severity="info"):
    severity = severity.lower()
    timestamp = datetime.datetime.now().strftime("%d%b%y - %H:%M:%S -> ")
    if severity == "dbg" or severity == "debug":
        app.logger.debug(f"\n-------> {timestamp} {entry} <------")
    elif severity == "warn" or severity == "warning":
        app.logger.warning(f"\n-------> {timestamp} {entry} <------")
    elif severity == "err" or severity == "error":
        app.logger.error(f"\n-------> {timestamp} {entry} <------")
    else:
        app.logger.info(f"\n-------> {timestamp} {entry} <------")

def secondsInHumanReadableTime(seconds):
    if seconds < 60:  # seconds
        return f"{seconds} seconds"
    if seconds < 3600:  # minutes
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins} minutes and {secs} seconds"
    if seconds < 86400:  # hours
        hours = seconds // 3600
        remainder = seconds % 3600
        if remainder > 60:
            mins = remainder // 60
            return f"{hours} hours and {mins} minutes"
        else:
            return f"{hours} hours"
    else:  # days
        days = seconds // 86400
        remainder = seconds % 86400
        if remainder < 3600:
            return f"{days} days"
        else:
            hours = remainder // 3600
            remainder2 = remainder % 3600
            if remainder2 > 60:
                minutes = remainder2 // 60
                return f"{days} days, {hours} hours and {minutes} minutes"
            else:
                return f"{days} days and {hours} hours"


def getHumanReadableSize(size):
    if size < 2 ** 10:  # byte
        return "%s bytes" % round(size, 2)
    elif size < 2 ** 20:  # kibibyte
        v = size / (2 ** 10)
        return "%sKiB" % round(v, 2)
    elif size < 2 ** 30:  # mebibyte
        v = size / (2 ** 20)
        return "%sMiB" % round(v, 2)
    elif size < 2 ** 40:  # gibibyte
        v = size / (2 ** 30)
        return "%sGiB" % round(v, 2)
    elif size < 2 ** 50:  # tebibyte
        v = size / (2 ** 40)
        return "%sTiB" % round(v, 2)
    else:  # pebibyte
        v = size / (2 ** 50)
        return "%sPiB" % round(v, 2)


def setMachineReadableSize(size, unit):
    if unit == "MiB":
        size = int(size) * 1024 * 1024
    elif unit == "GiB":
        size = int(size) * 1024 * 1024 * 1024
    elif unit == "TiB":
        size = int(size) * 1024 * 1024 * 1024 * 1024
    else:
        return None
    return size


def valueInMB(
    capacity,
):  # get input like 10.0GiB and returns 10240 (equivalent value in MB)
    unit = capacity[:-3]  # get last 3 letters (KiB / MiB / GiB / TiB / PiB)
    sizeInMB = float(capacity[0:-3])
    if unit == "KiB":
        return sizeInMB / 1024
    elif unit == "MiB":
        return sizeInMB
    elif unit == "GiB":
        return sizeInMB * 1024
    elif unit == "TiB":
        return sizeInMB * (1024 * 1024)
    elif unit == "PiB":
        return sizeInMB * (1024 * 1024 * 1024)
    else:  # value is in byte
        return sizeInMB / (1024 * 1024)

def checkHostPing(ip):
    import platform
    import subprocess
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    return subprocess.call(command) == 0


def checkHostHttps(ip):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    try:
        s.connect((ip, 443))
        s.shutdown(2)
        return True
    except:
        return False

def checkHostPort(ip, port):
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        return True
    except:
        return False

def check_password_valid(password):
    if len(password) < 8:
        return False
        # return false if password is less than 8 characters
    elif re.search(r"\d", password) is None:
        return False
        # return false if password does not contain digits
    elif re.search(r"[A-Z]", password) is None:
        return False
        # return false if password does not contain uppercase characters
    elif re.search(r"[a-z]", password) is None:
        return False
        # return false if password does not contain lowercase characters
    elif re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
        return False
        # return false if password does not contain lowercase characters
    else:
        return True


def checkSystemConnection(u):
    return checkHostHttps(u.ip_addr)


def dbg(obj, private="public"):
    """
    print object class and all attributes
    (also private if passed string "private" as argument)
    """
    import inspect

    class_name = obj.__class__.__name__
    print("Class: %s" % (class_name))
    members = inspect.getmembers(obj)
    for m in members:
        if private == "private" or not ((m[0][0:2] == "__") and (m[0][-2:-1] == "_")):
            print(m)



@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    db.init_app(app)
    port = environ['FLASK_PORT']
    debug = environ['FLASK_DEBUG']
    if ('CERTFILE' in list(environ.keys())) and ('CERTKEY' in list(environ.keys())):
        app.run(port=port, debug=debug, ssl_context=(environ['CERTFILE'],environ['CERTKEY']))
    else:
        app.run(port=port, debug=debug)