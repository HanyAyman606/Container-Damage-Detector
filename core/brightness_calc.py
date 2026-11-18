import cv2
import numpy as np

class BrightnessDetector:

    def __init__(self,thresh,std_thresh):
        self._image=None
        self.thresh=thresh
        self._bounds=None
        self.std_thresh=std_thresh


    @property
    def image(self):
        return self._image

    @image.setter
    def image(self,value):
        self._image=value

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, value):
        self._bounds=value
        self.start_x=value[0]
        self.end_x=value[1]
        


    def _extract_region(self):

        if self.image is None:
            raise ValueError("No image has been assigned")

        if self.bounds is None:
            raise ValueError("No region bounds have been assigned")

        if self.image.ndim == 3:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.image

        _, width = gray.shape

        start_x, end_x = self.bounds

        if start_x < 0 or end_x > width or start_x >= end_x:
            raise ValueError("Invalid X positions")

        image_region = gray[:, start_x:end_x]

        return image_region


    def Crest_or_Trough(self):

        region = self._extract_region()
        brightness = np.mean(region)
        return 'Crest' if brightness > self.thresh else 'Trough'


    def Holes_and_Tears(self):  # By testing homogeneity 

        region = self._extract_region()
        # Calculate brightness standard deviation
        std_dev = np.std(region)

        # Check homogeneity
        return std_dev >= self.std_thresh  # if True then there are Tears and Holes

    def calculate_damage_area(self, min_area=10):

        region = self._extract_region()
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(region, (5, 5), 0)

        # Apply Otsu thresholding
        _, binary = cv2.threshold(
            blurred, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Find contours
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Calculate total anomaly area
        anomaly_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            if area >= min_area:
                anomaly_area += area

        return anomaly_area