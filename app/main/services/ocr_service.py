import PIL  
import spacy
from spacy.symbols import ORTH
from spacy.tokens import Span
from flask import jsonify
import cv2
import pytesseract
import numpy as np
from ..models.invoice import Invoice, Vendor, Line
from ..models.invoice_encoder import InvoiceEncoder, VendorEncoder, DateEncoder, LineEncoder
from json import JSONEncoder
import json
import re
from spacy.matcher import Matcher,PhraseMatcher
from datetime import datetime
from spacy.pipeline import EntityRuler

errors = []

def get_invoice_data(image, language):
    text = get_text(image)
    doc = None
    nlp = None
    errors = []
    if(language == 'nld'):
        nlp = spacy.load("nl_core_news_sm")
    elif(language == 'fra'):
        nlp = spacy.load("fr_core_news_sm")
    elif(language == 'eng'):
        nlp = spacy.load("en_core_web_sm")
    nlp = add_entities(nlp)
    doc = nlp(text)
    return get_invoice(doc,nlp)

def get_invoice(doc, nlp):
    errors = []
    inv = Invoice()
    inv = get_dates(doc,nlp, inv)
    inv.vendor = get_vendor(doc,nlp)
    inv.number = get_number(doc)
    inv.currency = get_currency(doc)
    inv.discount = get_discount(doc, nlp)
    inv.vat = get_vat(doc,nlp)
    inv.subtotal = get_subtotal(doc, nlp)
    inv.total = get_total(doc, nlp)
    inv.lines = get_lines(doc,nlp)
    inv.errors = json.loads(json.dumps(errors))
    return json.loads(InvoiceEncoder().encode(inv))

def add_entities(nlp):
    ruler = EntityRuler(nlp,overwrite_ents = True)
    patterns = [{"label": "MONEY", "pattern": [{"TEXT" : {"REGEX": "^[0-9]*[,.][0-9]{2}$"}}]}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    return nlp

def get_vat(doc, nlp):
    return 21.23

def get_number(doc):
    return "45513312"

def get_currency(doc):
    errors.append("currency")
    return None

def get_discount(doc, nlp):
    return 25.20

def get_subtotal(doc, nlp):
    return 50.00

def get_total(doc, nlp):
    matcher = Matcher(nlp.vocab)
    pattern = [{"LOWER": "total"}]
    matcher.add("total", None, pattern)
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
    return 54.00

def get_lines(doc, nlp):
    lines = []
    line = Line()
    line.amount = 2000.00
    line.quantity = 20
    line.description = "stickers"
    line.unitPrice = 100.00
    lines.append(json.loads(LineEncoder().encode(line)))
    return json.loads(json.dumps(lines))


def get_dates(doc, nlp, invoice):
    dates= []
    expression = r"([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}"
    for match in re.finditer(expression, doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        if span is not None:
            obj = datetime.strptime(span.text,'%d/%m/%Y').date()
            dates.append(obj)
    if(len(dates) < 1):
        errors.append("dueDate")
        errors.append("invoiceDate")
        return invoice
    invoice.dueDate = json.loads(DateEncoder().encode(max(dates)))
    invoice.invoiceDate = json.loads(DateEncoder().encode(min(dates)))
    return invoice

def get_vendor(doc, nlp):
    vendor = Vendor()
    vendor.email = get_email_vendor(doc,nlp)
    vendor.name = get_name_vendor(doc,nlp)
    vendor.address = get_address_vendor(doc,nlp)
    vendor.phone = get_phone_vendor(doc,nlp)
    vendor.vatNumber = get_vatnumber_vendor(doc,nlp)
    return json.loads(VendorEncoder().encode(vendor))

def get_email_vendor(doc, nlp):
    return "example@example.com"

def get_name_vendor(doc, nlp):
    return "ing"

def get_address_vendor(doc, nlp):
    return "marktstraat 54, Antwerpen"

def get_phone_vendor(doc, nlp):
    return "0478 878 787"

def get_vatnumber_vendor(doc, nlp):
    expression = r"[A-Za-z]{2}[0-9|\s]{8,15}"
    for match in re.finditer(expression, doc.text):
        start, end = match.span()
        span = doc.char_span(start, end)
        if span is not None:
            return span.text.replace("\n", "")
    errors.append("vendor.vatNumber")
    return None

def get_entities(doc):
    ents = []
    for ent in doc.ents:
        ents.append({ent.text, ent.label_})
        """i = i + 1
        if len(doc) - 1 > i:
            ents.append({"text":token.text,"left_neighbour":doc[i-1].nbor().text ,"right_neighbour": doc[i].nbor().text})"""
    return ents

def convert_to_tiff(image):
    path = "./app/main/images/out.tiff"
    image = cv2.imread(image)
    cv2.imwrite(path, image)
    return cv2.imread(path)

def get_text(image):
    image = convert_to_tiff(image)
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(pre_processing(image),'eng+fra+nld', config=custom_config)
    
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def remove_noise(image):
    return cv2.medianBlur(image,5)
    
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
        
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 

def scale_image(image):
    scale_percent = 110
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    return cv2.resize(image,(width,height))

def pre_processing(image):
    pre_processed_img = scale_image(image)
    pre_processed_img = get_grayscale(pre_processed_img)
    pre_processed_img = deskew(pre_processed_img)   
    return pre_processed_img