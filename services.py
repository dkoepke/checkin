from contextlib import contextmanager
from psycopg2 import connect
from psycopg2.extras import DictCursor

import config
from models import Checkin


class DatabaseService(object):
    def __init__(self, host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, password=config.DB_PASSWORD,
                 database=config.DB_NAME):
        super(DatabaseService, self).__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._cxn = None

    @property
    def db(self):
        if self._cxn is None:
            self._cxn = connect(host=self.host, port=self.port,
                                user=self.user, password=self.password,
                                database=self.database,
                                cursor_factory=DictCursor)

        return self._cxn

    @contextmanager
    def cursor(self):
        db = self.db

        try:
            cur = db.cursor()
            yield cur
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            cur.close()

    def setup_tables(self):
        with self.cursor() as cur:
            cur.execute("""\
CREATE TABLE checkins (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    latitude    NUMERIC NOT NULL,
    longitude   NUMERIC NOT NULL,
    checkin_at  TIMESTAMP NOT NULL
)""")


class CheckinService(object):
    def __init__(self, db_svc):
        super(CheckinService, self).__init__()
        self.db_svc = db_svc

    def checkin(self, name, latitude, longitude):
        with self.db_svc.cursor() as cur:
            params = {
                'name': name,
                'latitude': latitude,
                'longitude': longitude,
            }
            cur.execute("""\
INSERT INTO checkins (name, latitude, longitude, checkin_at)
VALUES (%(name), %(latitude), %(longitude), NOW())""", params)

    def get_checkins(self, limit=None, skip=None):
        with self.db_svc.cursor() as cur:
            limit_and_offset = ""

            if limit:
                limit_and_offset += " LIMIT %d" % limit

            if skip:
                limit_and_offset += " OFFSET %d" % skip

            cur.execute("""\
SELECT id, name, latitude, longitude, checkin_at
FROM checkins
ORDER BY checkin_at DESC, id DESC""" + limit_and_offset)

            return [Checkin.from_dict(row) for row in cur]

        return []

    def get_recent_checkins(self, since_datetime=None):
        """Get checkins since a particular datetime.

        """
        with self._cursor() as cur:
            query = """\
SELECT c1.id, c1.name, c1.latitude, c1.longitude, c1.checkin_at
FROM checkins AS c1
INNER JOIN (
    SELECT id, MAX(checkin_at)
    FROM checkins
    GROUP BY name, id
) AS c2 ON c2.id = c1.id
"""
            params = {}

            if since_datetime:
                query += "WHERE c1.since > %(since_datetiem)\n"
                params['since_datetime'] = since_datetime

            query += 'ORDER BY c1.checkin_at DESC, id DESC'

            cur.execute(query, params)
            return cur.fetchall()

        return [Checkin.from_dict(row) for row in cur]


class AuthenticationService(object):
    def __init__(self):
        super(AuthenticationService, self).__init__()
        self.admin_users = {}

    def add_admin_user(self, username, password):
        self.admin_users[username] = password

    def authenticate(self, username, password):
        return self.admin_users.get(username, object()) == password
