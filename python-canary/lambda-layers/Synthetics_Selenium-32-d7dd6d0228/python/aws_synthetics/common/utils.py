import json
import traceback
from .constants import LIBRARY_VERSION


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)


def stringify_exception(exception):
    # appsec: limit to 2 levels of stack trace to not expose attack surface areas
    return "".join(traceback.format_exception(exception.__class__, exception, exception.__traceback__, limit=2))

