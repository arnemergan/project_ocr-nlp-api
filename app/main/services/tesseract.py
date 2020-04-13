from .opencv import OpenCV
import pytesseract
from ..models.invoice import BoxValue
from pytesseract import Output

class Tesseract:
    _cv = None

    def __init__(self):
        self._cv = OpenCV()
    
    def get_data(self,image):
        custom_config = r'--oem 3 --psm 6'
        image = self._cv.convert_to_tiff(image)
        return pytesseract.image_to_data(self._cv.pre_processing(image),'eng+fra+nld', config=custom_config,output_type=Output.DICT)

    def get_string(self,image):
        custom_config = r'--oem 3 --psm 6'
        image = self._cv.convert_to_tiff(image)
        return pytesseract.image_to_string(self._cv.pre_processing(image),'eng+fra+nld', config=custom_config,output_type=Output.DICT)
        
    def get_boxes(self,image):
        boxes = []
        data = self.get_data(image)
        lines = data["line_num"]
        for i in range(len(lines)):
            if int(data["conf"][i]) > -1:
                boxes.append(BoxValue(data["text"][i],int(data["conf"][i]),int(lines[i])))
        return boxes