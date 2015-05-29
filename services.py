from contextlib import contextmanager

from models import Checkin


class CheckinService(object):
    def __init__(self, db):
        super(CheckinService, self).__init__()
        self.db = db

    @contextmanager
    def _cursor(self):
        try:
            cur = self.db.cursor()
            yield cur
            self.db.commit()
        finally:
            self.db.rollback()
            cur.close()

    def checkin(self, name, longitude, latitude):
        with self._cursor() as cur:
            params = {
                'name': name,
                'longitude': longitude,
                'latitude': latitude,
            }
            cur.execute("""\
INSERT INTO checkins (name, longitude, latitude, when)
VALUES (%(name), %(longitude), %(latitude))""", params)

    def get_checkins(self, limit=None, skip=None):
        with self._cursor() as cur:
            limit_and_offset = ""

            if limit:
                limit_and_offset += " LIMIT %d" % limit

            if skip:
                limit_and_offset += " OFFSET %d" % skip

            cur.execute("""\
SELECT id, name, longitude, latitude, "when"
FROM checkins
ORDER BY "when" DESC, id DESC""" + limit_and_offset)

            return [Checkin.from_dict(row) for row in cur]

        return []

    def get_recent_checkins(self, since_datetime=None):
        """Get checkins since a particular datetime.

        """
        with self._cursor() as cur:
            query = """\
SELECT c1.id, c1.name, c1.longitude, c1.latitude, c1."when"
FROM checkins AS c1
INNER JOIN (
    SELECT id, MAX("when")
    FROM checkins
    GROUP BY name, id
) AS c2 ON c2.id = c1.id
"""
            params = {}

            if since_datetime:
                query += "WHERE c1.since > %(since_datetiem)\n"
                params['since_datetime'] = since_datetime

            query += 'ORDER BY c1."when" DESC, id DESC'

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
