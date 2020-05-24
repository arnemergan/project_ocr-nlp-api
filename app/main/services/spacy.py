from spacy.pipeline import EntityRuler
import spacy
from ..models.invoice import Invoice, Vendor, Line, BoxValue, Value
from spacy.symbols import ORTH
from spacy.tokens import Span
from spacy.matcher import Matcher,PhraseMatcher
from json import JSONEncoder
import json
import re
from datetime import datetime

class Spacy:

    _nlp = None
    _doc = None
    _entityruler = None

    def __init__(self,language):
        if(language == 'nld'):
            self._nlp = spacy.load("nl_core_news_sm")
        elif(language == 'fra'):
            self._nlp = spacy.load("fr_core_news_sm")
        else:
            self._nlp = spacy.load("en_core_web_sm")
        self._entityruler = EntityRuler(self._nlp,overwrite_ents = True)
        self.add_entities()

    def add_entities(self):
        patterns = []
        patterns.append({"label": "DATE", "pattern":[{'TEXT': {"REGEX":"^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$"}}]})
        patterns.append({"label":"MONEY","pattern":[{'TEXT':{"REGEX":"^[0-9]+(\.[0-9]{1,2})?$"}}]})
        self._entityruler.add_patterns(patterns)
        self._nlp.add_pipe(self._entityruler)

    def get_invoice(self, text):
        self._doc = self._nlp(text)
        return self.load_invoice()
    
    def load_invoice(self):
        self.get_entities()
        return Invoice(
            vendor=Vendor(name=Value("",0,"ORG"),address=Value("",0,"ADDRESS"),email=Value("",0,"EMAIL"),phone=Value("",0,"PHONE"),vatNumber=self.get_vatnumber()),
            lines=self.get_lines(),
            subtotal=self.get_subtotal(),
            total=self.get_total(),
            vat=Value(0,0,"VAT"),
            number=Value("",0,"NUMBER"),
            currency=Value("",0,"CURRENCY"),
            dueDate=self.get_due_date(),
            invoiceDate=self.get_invoice_date()
        )
    
    def get_lines(self):
        lines = []
        lines.append(Line(amount=Value(0.0,0.0,""),quantity=Value(0.0,0.0,""),description=Value("",0.0,""),unitPrice=Value(0.0,0.0,"")))
        return lines

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
                    return Value(right.text,0.50,"TOTAL")
        return Value('',0,"TOTAL")

    def get_subtotal(self):
        matcher = Matcher(self._nlp.vocab)
        pattern = [{"LOWER": "subtotal"}]
        matcher.add("subtotal", None, pattern)
        matches = matcher(self._doc)
        for match_id, start, end in matches:
            string_id = self._nlp.vocab.strings[match_id]
            span = self._doc[start:end]
            for right in span.rights:
                if right.like_num:
                    return Value(right.text,0.50,"SUBTOTAL")
        return Value('',0,"SUBTOTAL")
    
    def get_vatnumber(self):
        expression = r"[A-Za-z]{2}[0-9|\s]{8,15}"
        for match in re.finditer(expression, self._doc.text):
            start, end = match.span()
            span = self._doc.char_span(start, end)
            if span is not None:
                return Value(span.text.replace("\n", ""),0.5,"VATNUMBER")
        return Value('',0,"VATNUMBER")

    def get_due_date(self):
        dates = []
        expression = r"([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}"
        for match in re.finditer(expression, self._doc.text):
            start, end = match.span()
            span = self._doc.char_span(start, end)
            if span is not None:
                obj = datetime.strptime(span.text,'%d/%m/%Y').date()
                dates.append(obj)
        if(len(dates) > 0):
            return Value(max(dates),0.5,"DATE")
        return Value("",0.0,"DATE")

    def get_invoice_date(self):
        dates = []
        expression = r"([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}"
        for match in re.finditer(expression, self._doc.text):
            start, end = match.span()
            span = self._doc.char_span(start, end)
            if span is not None:
                obj = datetime.strptime(span.text,'%d/%m/%Y').date()
                dates.append(obj)
        if(len(dates) > 0):
            return Value(min(dates),0.5,"DATE")
        return Value("",0.0,"DATE")

    def get_entities(self):
        ents = []
        for ent in self._doc.ents:
            if ent.label_ == "MONEY":
                print({ent.text, ent.label_})
            elif ent.label_ == "DATE":
                print({ent.text, ent.label_})
            elif ent.label == "VATNUMBER":
                print({ent.text, ent.label_})
            elif ent.label == "VENDOR_ADDRESS":
                print({ent.text, ent.label_})
            elif ent.label == "VENDOR_NAME":
                print({ent.text, ent.label_})
            elif ent.label == "TOTAL":
                print({ent.text, ent.label_})
            elif ent.label == "SUBTOTAL":
                print({ent.text, ent.label_})

        