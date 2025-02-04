import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def apply_effects(image, brightness=0, contrast=1.0, blur=0):
        """Apply all effects in a single pass"""
        if image is None:
            return None
            
        result = image.copy()
        
        # Apply brightness
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow
            result = cv2.addWeighted(result, alpha_b, result, 0, gamma_b)
        
        # Apply contrast
        if contrast != 1.0:
            result = cv2.convertScaleAbs(result, alpha=contrast, beta=0)
        
        # Apply blur
        if blur > 0:
            ksize = blur * 2 + 1
            result = cv2.GaussianBlur(result, (ksize, ksize), 0)
            
        return result

    @staticmethod
    def resize_image(image, scale_percent, use_high_quality=True):
        """Resize image by percentage"""
        if image is None:
            return None
            
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        
        interpolation = cv2.INTER_LANCZOS4 if use_high_quality else cv2.INTER_LINEAR
        return cv2.resize(image, (width, height), interpolation=interpolation)

    @staticmethod
    def crop_image(image, x1, y1, x2, y2):
        """Crop image to specified coordinates"""
        if image is None:
            return None
            
        return image[y1:y2, x1:x2].copy()
