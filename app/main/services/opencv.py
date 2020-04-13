import cv2
import numpy as np
import PIL  

class OpenCV:
    def convert_to_tiff(self,image):
        path = "./app/main/images/out.tiff"
        image = cv2.imread(image)
        cv2.imwrite(path, image)
        return cv2.imread(path)
        
    def get_grayscale(self,image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def remove_noise(self,image):
        return cv2.medianBlur(image,5)
        
    def thresholding(self,image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def deskew(self,image):
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

    def scale_image(self,image):
        scale_percent = 110
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        return cv2.resize(image,(width,height))

    def pre_processing(self,image):
        pre_processed_img = self.scale_image(image)
        pre_processed_img = self.get_grayscale(pre_processed_img)
        pre_processed_img = self.deskew(pre_processed_img)   
        pre_processed_img = self.thresholding(pre_processed_img)
        return pre_processed_img