from flask import Flask, render_template, request, Response
from functools import wraps
from os import getenv
from psycopg2 import connect

app = Flask(__name__)


ADMIN_USER = getenv('CHECKIN_ADMIN_USER', 'admin')
ADMIN_PASSWORD = getenv('CHEKIN_ADMIN_PASSWORD', object())


DB_HOST = getenv('CHECKIN_DB_HOST', 'localhost')
DB_PORT = int(getenv('CHECKIN_DB_PORT', 5432))
DB_USER = getenv('CHECKIN_DB_USER')
DB_PASSWORD = getenv('CHECKIN_DB_PASSWORD')
DB_NAME = getenv('CHECKIN_DB_NAME')

DB = connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD,
             host=DB_HOST, port=DB_PORT)


try:
    cur = DB.cursor()
    cur.execute("""\
CREATE TABLE checkins (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    longitude   NUMERIC NOT NULL,
    latitude    NUMERIC NOT NULL,
    when        TIMESTAMP NOT NULL
)""")
except:
    pass


def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASSWORD


def authenticate():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    try:
        cur = DB.cursor()
        cur.execute("""\
INSERT INTO checkins (name, longitude, latitude, when) \
VALUES (%(name), %(longitude), %(latitude), NOW())""", data)
        cur.close()
    except:
        pass


@app.route('/admin')
@requires_auth
def admin():
    try:
        cur = DB.cursor()
        cur.execute("""\
SELECT id, name, longitude, latitude, when
FROM checkins
ORDER BY when DESC""")
        checkins = cur.fetchall()
    except:
        checkins = []

    return render_template('admin.html', {'checkins': checkins})
