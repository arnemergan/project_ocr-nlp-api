from flask import jsonify
from ..models.invoice import Invoice, Vendor, Line, BoxValue
from ..models.invoice_encoder import InvoiceEncoder, VendorEncoder, DateEncoder, LineEncoder
from json import JSONEncoder
import json
from .tesseract import Tesseract
from .spacy import Spacy

class Ocr_Service:

    errors = []
    tesseract = None
    spacy = None
    invoice = None
    _text_array = []
    
    def __init__(self,language):
        self.errors = []
        self.tesseract = Tesseract()
        self.spacy = Spacy(language)
        self.invoice = Invoice()
        self._text_array = []

    def get_invoice_data(self, image):
        self.errors.clear()
        boxes = self.tesseract.get_boxes(image)
        for i in range(boxes[len(boxes)-1].number + 1):
            text = ""
            filter_boxes = filter(lambda x: x.number == i, boxes)
            for box in filter_boxes:
                text = text + " " + box.text
            self._text_array.append(text)
        if(self.validate_invoice()):
            self.invoice = self.spacy.get_invoice(self._text_array)
            self.invoice.errors = json.loads(json.dumps(self.errors))
        return json.loads(InvoiceEncoder().encode(self.invoice))
    
    def validate_invoice(self):
        if self.invoice.currency == "": 
            self.errors.append("currency")
        return True