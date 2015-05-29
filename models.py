class Checkin(object):
    def __init__(self):
        super(Checkin, self).__init__()
        self.id = None
        self.name = None
        self.longitude = None
        self.latitude = None
        self.when = None

    @classmethod
    def from_dict(cls, a_dict):
        it = Checkin()
        it.id = a_dict['id']
        it.name = a_dict['name']
        it.longitude = a_dict['longitude']
        it.latitude = a_dict['latitude']
        it.when = a_dict['when']
        return it
