from flask import jsonify
from ..models.invoice import Vendor, Line, BoxValue, Invoice
from ..models.invoice_encoder import InvoiceEncoder, VendorEncoder, DateEncoder, LineEncoder
from json import JSONEncoder
import json
from .tesseract import Tesseract
from .spacy import Spacy
from random import random
import os
import io
from PIL import Image
import pytesseract
from wand.image import Image as wi
import string

class Ocr_Service:

    tesseract = None
    spacy = None
    
    def __init__(self,language):
        self.tesseract = Tesseract()
        self.spacy = Spacy(language)
    
    def get_invoice_data_pdf(self,pdf):
        pdfFile = wi(filename = pdf, resolution = 300)
        image = pdfFile.convert('jpeg')
        imageBlobs = []
        for img in image.sequence:
            imgPage = wi(image = img)
            imageBlobs.append(imgPage.make_blob('jpeg'))
        text = ""
        for imgBlob in imageBlobs:
            text = text + " " + self.tesseract.get_string_pdf(Image.open(io.BytesIO(imgBlob)))
        return json.loads(json.dumps(self.spacy.get_invoice(text)))

    def get_invoice_data(self, image):
        return json.loads(json.dumps(self.spacy.get_invoice(self.tesseract.get_string(image))))

    def get_invoice_data_boxes(self, image):
        boxtext = ""
        boxes = self.tesseract.get_boxes(image)
        for i in range(boxes[len(boxes)-1].number + 1):
            text = ""
            filter_boxes = filter(lambda x: x.number == i, boxes)
            for box in filter_boxes:
                text = text + " " + box.text
            boxtext = boxtext + " " + text
        return json.loads(json.dumps(self.spacy.get_invoice(self.tesseract.get_string(image))))