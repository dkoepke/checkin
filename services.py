from contextlib import contextmanager


class CheckinService(object):
    def __init__(self, db):
        super(CheckinService, self).__init__()
        self.db = db

    @contextmanager
    def _cursor(self):
        try:
            cur = self.db.cursor()
            yield cur
        finally:
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
SELECT id, name, longitude, latitude, when
FROM checkins
ORDER BY when DESC, id DESC""" + limit_and_offset)

            return cur.fetchall()

        return []

    def get_recent_checkins(self, since_datetime):
        """Get checkins since a particular datetime.

        """
        with self._cursor() as cur:
            cur.execute("""\
SELECT id, name, longitude, latitude, when
FROM checkins
WHERE since > %(since_datetiem)
ORDER BY when DESC, id DESC""", {'since_datetiem': since_datetime})
            return cur.fetchall()

        return []


def AuthenticationService(object):
    def __init__(self):
        super(AuthenticationService, self).__init__()
        self.admin_users = {}

    def add_admin_user(self, username, password):
        self.admin_users[username] = password

    def authenticate(self, username, password):
        return bool(
            username in self.admin_users and
            self.admin_users[username] == password)
