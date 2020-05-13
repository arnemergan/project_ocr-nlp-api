from spacy.pipeline import EntityRuler
import spacy
from ..models.invoice import Invoice, Vendor, Line, BoxValue
from spacy.symbols import ORTH
from spacy.tokens import Span
from spacy.matcher import Matcher,PhraseMatcher
from ..models.invoice_encoder import InvoiceEncoder, VendorEncoder, DateEncoder, LineEncoder
from json import JSONEncoder
import json
import re
from datetime import datetime

class Spacy:

    _nlp = None
    _doc = None
    _entityruler = None
    _invoice = None
    money = []
    dates = []

    def __init__(self,language):
        """if(language == 'nld'):
            self._nlp = spacy.load("nl_core_news_sm")
        elif(language == 'fra'):
            self._nlp = spacy.load("fr_core_news_sm")
        else:
            self._nlp = spacy.load("en_core_web_sm")"""
        self._nlp = spacy.load("D:\\School\\FINAL_WORK\\Git\\nlp_ocr_api\\API-ocr-nlp_final-work\\spacy_training\\Invoicing")
        self.money.clear()
        self.dates.clear()
        """self._entityruler = EntityRuler(self._nlp,overwrite_ents = True)
        self.add_entities()"""
        self._invoice = Invoice()

    def add_entities(self):
        patterns = []
        patterns.append({"label": "DATE", "pattern":[{'TEXT': {"REGEX":"^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$"}}]})
        patterns.append({"label":"MONEY","pattern":[{'TEXT':{"REGEX":"^[0-9]+(\.[0-9]{1,2})?$"}}]})
        self._entityruler.add_patterns(patterns)
        self._nlp.add_pipe(self._entityruler)

    def get_invoice(self,text_array):
        for text in text_array:
            self._doc = self._nlp(text)
            self.load_invoice()

        for money in self.money:
            """print(money)"""

        for date in self.dates:
            """print(date)"""

        return self._invoice

    def load_invoice(self):
        self.get_entities()
        self.get_dates()
        self.get_vendor()
        self.get_number()
        self.get_currency()
        self.get_discount()
        self.get_vat()
        self.get_subtotal()
        self.get_total()
        self.get_lines()

    def get_vat(self):
        self._invoice.vat = 21

    def get_number(self):
        self._invoice.number = "4533321"

    def get_currency(self):
        self._invoice.currency = "eur"

    def get_discount(self):
        self._invoice.discount = 45

    def get_subtotal(self):
        self._invoice.subtotal = 45.23

    def get_total(self):
        matcher = Matcher(self._nlp.vocab)
        pattern = [{"LOWER": "total"}]
        matcher.add("total", None, pattern)
        matches = matcher(self._doc)
        for match_id, start, end in matches:
            string_id = self._nlp.vocab.strings[match_id]
            span = self._doc[start:end]
            for right in span.rights:
                if right.like_num:
                    self._invoice.total = right.text

    def get_lines(self):
        lines = []
        line = Line()
        line.amount = 2000.00
        line.quantity = 20
        line.description = "stickers"
        line.unitPrice = 100.00
        lines.append(json.loads(LineEncoder().encode(line)))
        self._invoice.lines = json.loads(json.dumps(lines))


    def get_dates(self):
        dates= []
        expression = r"([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}"
        for match in re.finditer(expression, self._doc.text):
            start, end = match.span()
            span = self._doc.char_span(start, end)
            if span is not None:
                obj = datetime.strptime(span.text,'%d/%m/%Y').date()
                dates.append(obj)
        if(len(dates) > 0):
            self._invoice.dueDate = json.loads(DateEncoder().encode(max(dates)))
            self._invoice.invoiceDate = json.loads(DateEncoder().encode(min(dates)))

    def get_vendor(self):
        vendor = Vendor()
        vendor.email = self.get_email_vendor()
        vendor.name = self.get_name_vendor()
        vendor.address = self.get_address_vendor()
        vendor.phone = self.get_phone_vendor()
        vendor.vatNumber = self.get_vatnumber_vendor()
        self._invoice.vendor =  json.loads(VendorEncoder().encode(vendor))

    def get_email_vendor(self):
        return "example@example.com"

    def get_name_vendor(self):
        return "ing"

    def get_address_vendor(self):
        return "marktstraat 54, Antwerpen"

    def get_phone_vendor(self):
        return "0478 878 787"

    def get_vatnumber_vendor(self):
        expression = r"[A-Za-z]{2}[0-9|\s]{8,15}"
        for match in re.finditer(expression, self._doc.text):
            start, end = match.span()
            span = self._doc.char_span(start, end)
            if span is not None:
                return span.text.replace("\n", "")
        return None

    def get_entities(self):
        ents = []
        for ent in self._doc.ents:
            print({ent.text, ent.label_})
            if ent.label_ == "MONEY":
                self.money.append(ent.text)
                """print({ent.text, ent.label_})"""
            elif ent.label_ == "DATE":
                self.dates.append(ent.text)
                """print({ent.text, ent.label_})"""
            elif ent.label_ == "PROCENT":
               """print({ent.text, ent.label_})"""
            

        