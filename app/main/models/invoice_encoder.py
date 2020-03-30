from json import JSONEncoder
import json
from .invoice import Invoice, Vendor, Line
import datetime

class DateEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, (datetime.date, datetime.datetime)):
            return object.isoformat()
        else:
            return json.JSONEncoder.default(self, object)

class InvoiceEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Invoice):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)

class VendorEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Vendor):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)

class LineEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Line):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)