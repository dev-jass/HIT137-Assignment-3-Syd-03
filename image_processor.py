import cv2
import numpy as np
from PIL import Image, ImageTk

class ImageProcessor:
    """
    Handles image loading, processing (crop, resize, filter),
    and undo/redo history management.
    """
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.history = []
        self.redo_stack = []
        self.max_history = 10

    def load_image(self, filepath):
        """
        Loads an image from the given file path.
        Returns an ImageTk.PhotoImage if successful, otherwise None.
        """
        try:
            # Attempt to read the image with OpenCV
            image = cv2.imread(filepath)
            if image is None:
                return None  # Means OpenCV couldn't read the file
            self.original_image = image
            self.current_image = image.copy()
            self._add_to_history()
            return self._convert_to_photo()
        except Exception:
            return None

    def crop_image(self, start_x, start_y, end_x, end_y):
        """
        Crops the current image using the given bounding box.
        Returns an ImageTk.PhotoImage or None if invalid.
        """
        if self.current_image is None:
            return None

        # Ensure coordinates are in correct order
        min_x, max_x = sorted([start_x, end_x])
        min_y, max_y = sorted([start_y, end_y])

        # Ensure coordinates are within image boundaries
        h, w = self.current_image.shape[:2]
        min_x, min_y = max(0, min_x), max(0, min_y)
        max_x, max_y = min(w, max_x), min(h, max_y)

        # Check for non-zero area
        if max_x - min_x <= 0 or max_y - min_y <= 0:
            return None  # Invalid crop area

        self.current_image = self.current_image[min_y:max_y, min_x:max_x]
        self._add_to_history()
        return self._convert_to_photo()

    def resize_image(self, scale_percent):
        """
        Resizes the current image by scale_percent (1-500).
        Returns an ImageTk.PhotoImage or None.
        """
        if self.current_image is None or scale_percent <= 0:
            return None

        scale_percent = max(1, min(500, scale_percent))  # clamp 1..500
        width = max(1, int(self.current_image.shape[1] * scale_percent / 100))
        height = max(1, int(self.current_image.shape[0] * scale_percent / 100))

        self.current_image = cv2.resize(self.current_image, (width, height))
        self._add_to_history()
        return self._convert_to_photo()

    def save_image(self, filepath):
        """
        Saves the current image to the given filepath.
        Returns True on success, False otherwise.
        """
        if self.current_image is None:
            return False
        try:
            cv2.imwrite(filepath, self.current_image)
            return True
        except Exception:
            return False

    def apply_filter(self, filter_type):
        """
        Applies a basic filter (blur, sharpen, grayscale).
        Returns an ImageTk.PhotoImage or None.
        """
        if self.current_image is None:
            return None

        if filter_type == "blur":
            self.current_image = cv2.GaussianBlur(self.current_image, (5, 5), 0)
        elif filter_type == "sharpen":
            kernel = np.array([[-1, -1, -1],
                               [-1,  9, -1],
                               [-1, -1, -1]])
            self.current_image = cv2.filter2D(self.current_image, -1, kernel)
        elif filter_type == "grayscale":
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            self.current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        self._add_to_history()
        return self._convert_to_photo()

    def undo(self):
        """
        Undoes the last image operation if possible.
        Returns an ImageTk.PhotoImage or None.
        """
        if len(self.history) > 1:
            # Move current image to redo stack
            self.redo_stack.append(self.history.pop())
            # Restore the previous image
            self.current_image = self.history[-1].copy()
            return self._convert_to_photo()
        return None

    def redo(self):
        """
        Redoes an undone operation if available.
        Returns an ImageTk.PhotoImage or None.
        """
        if self.redo_stack:
            # Move forward again
            self.history.append(self.redo_stack.pop())
            self.current_image = self.history[-1].copy()
            return self._convert_to_photo()
        return None

    def _convert_to_photo(self):
        """
        Converts the current BGR image to an RGB ImageTk.PhotoImage.
        """
        if self.current_image is None:
            return None
        rgb_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        return ImageTk.PhotoImage(pil_image)

    def _add_to_history(self):
        """
        Adds the current image to the history stack and clears the redo stack.
        Enforces max_history to keep memory usage in check.
        """
        self.history.append(self.current_image.copy())
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.redo_stack.clear()