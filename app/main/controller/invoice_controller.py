import os
from flask import current_app, Flask, request, redirect, jsonify
from ..services.ocr_service import get_invoice_data
from werkzeug.utils import secure_filename
from ..util.invoiceDto import InvoiceDto
from flask_restplus import Resource

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_LANGUAGES = set(['nld','eng','fra'])

api = InvoiceDto.api
_image =InvoiceDto.upload_parser

def allowed_languages(language):
    return language in ALLOWED_LANGUAGES

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/ocr')
class invoice_controller(Resource):
    @api.doc('get invoice data')
    @api.expect(_image, validate=True)
    def post(self):
        if 'image' not in request.files:
            resp = jsonify({'message' : 'No image selected!'})
            resp.status_code = 400
            return resp
        
        file = request.files['image']
        lang = request.args.get('language')

        if not allowed_languages(lang):
            resp = jsonify({'message' : 'Not a valid language!'})
            resp.status_code = 400
            return resp

        if file.filename == '':
            resp = jsonify({'message' : 'No image selected!'})
            resp.status_code = 400
            return resp

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'] , filename))
            resp = jsonify({'output' : get_invoice_data(os.path.join(current_app.config['UPLOAD_FOLDER'] , filename),lang)})
            resp.status_code = 200
            return resp
        else:
            resp = jsonify({'message' : 'Allowed file types are pdf, png, jpg, jpeg, gif'})
            resp.status_code = 400
        return resp
