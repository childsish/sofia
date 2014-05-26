import json

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)
        elif hasattr(obj, 'vs'):
            obj = {str(k): v for k, v in obj.vs.iteritems()}
        return json.JSONEncoder.default(self, obj)
