


class BidirectionalDict(dict):

    def __init__(self, d : dict = None):
        super().__init__()
        if d:
            for key, val in d.items():
                self[key] = val


    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        dict.__setitem__(self, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)