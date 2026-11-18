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

    def calculate_damage_area(self, debug_image=None, min_area=10):

        region = self._extract_region()

        blurred = cv2.GaussianBlur(region, (5, 5), 0)

        # First Otsu pass: splits histogram into dark vs bright classes
        otsu_thresh, _ = cv2.threshold(
            blurred, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        dark_pixels  = blurred[blurred <= otsu_thresh]
        bright_pixels = blurred[blurred > otsu_thresh]

        if len(dark_pixels) > len(bright_pixels):
            # Trimodal case (hole + wall + text/stickers).
            # A single Otsu threshold lumps the wall and hole together so the
            # contour brightness test always fails.  Apply a second Otsu on
            # just the dark half to isolate the hole from the wall.
            hole_thresh, _ = cv2.threshold(
                dark_pixels, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            wall_band = blurred[(blurred > hole_thresh) & (blurred <= otsu_thresh)]
            majority_brightness = np.mean(wall_band) if wall_band.size > 0 \
                                   else np.mean(dark_pixels)
            # Binary mask: pixels at or below the hole sub-threshold are "dark"
            binary = (blurred <= hole_thresh).astype(np.uint8) * 255
        else:
            # Bimodal case (wall vs hole) — single Otsu is sufficient
            majority_brightness = np.mean(bright_pixels)
            binary = (blurred <= otsu_thresh).astype(np.uint8) * 255

        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        anomaly_area = 0
        start_x, _ = self.bounds

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < min_area:
                continue

            mask = np.zeros(region.shape, dtype=np.uint8)

            cv2.drawContours(
                mask, [contour], -1, 255, cv2.FILLED
            )

            contour_brightness = cv2.mean(region, mask=mask)[0]

            if contour_brightness < majority_brightness:

                anomaly_area += area

                if debug_image is not None:
                    cv2.drawContours(
                        debug_image,
                        [contour],
                        -1,
                        (255, 255, 0),
                        2,
                        offset=(start_x, 0)
                    )

        return anomaly_area