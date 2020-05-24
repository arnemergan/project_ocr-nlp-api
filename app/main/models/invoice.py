class Line(dict):
    def __init__(self, amount, quantity, description, unitPrice):
        dict.__init__(self, amount=amount, quantity=quantity, description=description,unitPrice=unitPrice)

class Vendor(dict):
    def __init__(self, name, address, email, phone, vatNumber):
        dict.__init__(self, name=name, address=address, email=email,phone=phone, vatNumber=vatNumber)

class Invoice(dict):
    def __init__(self, vendor, lines, number, dueDate, invoiceDate, currency, vat, subtotal, total):
        dict.__init__(self,lines=lines ,vendor=vendor,number=number, dueDate=dueDate, invoiceDate=invoiceDate,currency=currency, vat=vat,subtotal=subtotal, total=total)

class Value(dict):
    def __init__(self, value, confidence, label):
        dict.__init__(self, value=value, confidence=confidence, label=label)
    
    def default(self):
        dict.__init__(self, value='', confidence=0, label='')

class BoxValue():
    def __init__(self,text,confidence,number):
        self.confidence = confidence
        self.text = text
        self.number = number
