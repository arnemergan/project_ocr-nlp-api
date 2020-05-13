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
    
    def get_invoice_data_pdf(self,pdf,filename):
        pdfFile = wi(filename = pdf, resolution = 300)
        image = pdfFile.convert('jpeg')

        imageBlobs = []
        
        for img in image.sequence:
            imgPage = wi(image = img)
            imageBlobs.append(imgPage.make_blob('jpeg'))

        extract = []

        for imgBlob in imageBlobs:
            image = Image.open(io.BytesIO(imgBlob))
            text = self.tesseract.get_string_pdf(image)
            self.save_image(filename,text)

    def get_invoice_data(self, image,filename):
        self.errors.clear()
        self.save_image(filename,self.tesseract.get_string(image))
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
    
    def save_image(self,filename,text):
        self.errors.clear()
        text_file = open(os.path.join("D:\\School\\FINAL_WORK\\Git\\nlp_ocr_api\\API-ocr-nlp_final-work\\spacy_training\\", filename + str(random()) + ".py"), "w")
        n = text_file.write(text)
        text_file.close()

    def convert_dataturks_to_spacy(self,dataturks_JSON_FilePath):
        try:
            training_data = []
            lines=[]
            with open(dataturks_JSON_FilePath, 'r') as f:
                lines = f.readlines()

            for line in lines:
                parsed_json = (json.loads(line))
                text =  ''.join([i if ord(i) < 128 else ' ' for i in parsed_json["content"].replace('\n','')])
                entities = []
                if parsed_json["annotation"] != None:
                    for annotation in parsed_json["annotation"]:
                        #only a single point in text annotation.
                        point = annotation["points"][0]
                        labels = annotation["label"]
                        # handle both list of labels or a single label.
                        if not isinstance(labels, list):
                            labels = [labels]

                        for label in labels:
                            #dataturks indices are both inclusive [start, end] but spacy is not [start, end)
                            entities.append((point['start'], point['end'] + 1 ,label))
                    training_data.append((text, {"entities" : entities}))
            return training_data
        except Exception as e:
           print("Unable to process " + dataturks_JSON_FilePath + "\n" + "error = " + str(e))
           return None