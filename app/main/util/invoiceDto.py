from flask_restplus import Namespace, fields
from werkzeug.datastructures import FileStorage

class InvoiceDto:
    api = Namespace('factuur', description='')
    upload_parser = api.parser()
    upload_parser.add_argument('language',required=True)
    upload_parser.add_argument('image', location='files',type=FileStorage, required=True)
    