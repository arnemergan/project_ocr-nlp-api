from flask_restplus import Api,Namespace
from flask import Blueprint

from .main.controller.invoice_controller import api as invoice_ns


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='FACTUUR RESTFULL API',
          version='1.0',
          description='De api krijgt een afbeelding van een factuur en probeert door middel van nlp en ocr de data eruit te extraheren'
          )

api.add_namespace(invoice_ns, path='/api/v1')