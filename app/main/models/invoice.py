class Line():
    def __init__(self):
        self.amount = None
        self.quantity = None
        self.description = None
        self.unitPrice = None

    def constructor(self,amount,quantity,description,unitPrice):
        self.amount = amount
        self.quantity = quantity
        self.description = description
        self.unitPrice = unitPrice

class Vendor():
    def __init__(self): 
        self.name = None
        self.address = None
        self.email = None 
        self.phone = None
        self.vatNumber = None

    def constructor(self,name,address,email,phone,vatNumber):
        self.name = name
        self.address = address
        self.email = email
        self.phone = phone
        self.vatNumber = vatNumber        

class Invoice():
    def __init__(self):
        self.number = None
        self.dueDate = None
        self.invoiceDate = None
        self.currency = None
        self.vendor = Vendor()
        self.discount = None
        self.vat = None
        self.subtotal = None
        self.total = None
        self.lines = []
        self.errors = []
    
    def constructor(self, number, dueDate, invoiceDate, currency, vendor, discount, vat, total, subtotal, lines, errors):
        self.number = number
        self.dueDate = dueDate
        self.invoiceDate = invoiceDate
        self.currency = currency
        self.vendor = vendor
        self.discount = discount
        self.vat = vat
        self.subtotal = subtotal
        self.total = total
        self.lines = lines
        self.errors = errors