from flask import Flask, render_template, request, Response
from functools import wraps
from os import getenv
from psycopg2 import connect

from services import AuthenticationService, CheckinService

app = Flask(__name__)


ADMIN_USER = getenv('CHECKIN_ADMIN_USER', 'admin')
ADMIN_PASSWORD = getenv('CHECKIN_ADMIN_PASSWORD', object())

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

auth_svc = AuthenticationService()
auth_svc.add_admin_user(ADMIN_USER, ADMIN_PASSWORD)

checkin_svc = CheckinService(DB)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth_svc.authenticate(auth.username, auth.password):
            return Response('Could not verify your access level for that URL.\n'
                            'You have to login with proper credentials', 401,
                            {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated


@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    try:
        checkin_svc.checkin(data['name'], data['longitude'], data['latitude'])
    except:
        pass


@app.route('/admin')
@requires_auth
def admin():
    checkins = checkin_svc.get_checkins()
    return render_template('admin.html', {'checkins': checkins})


if __name__ == '__main__':
    app.run()
