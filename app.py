from flask import Flask, render_template, request, Response
from functools import wraps

from config import ADMIN_USER, ADMIN_PASSWORD, GOOGLE_API_KEY
from services import AuthenticationService, CheckinService, DatabaseService

app = Flask(__name__)


db_svc = DatabaseService()
db_svc.setup_tables()

auth_svc = AuthenticationService()
auth_svc.add_admin_user(ADMIN_USER, ADMIN_PASSWORD)

checkin_svc = CheckinService(db_svc)


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
    data = request.form

    try:
        checkin_svc.checkin(data['name'], data['lat'], data['lng'])
    except:
        pass


@app.route('/admin')
@requires_auth
def admin():
    checkins = checkin_svc.get_checkins()
    return render_template('admin.html', checkins=checkins, google_api_key=GOOGLE_API_KEY)


if __name__ == '__main__':
    app.run()
