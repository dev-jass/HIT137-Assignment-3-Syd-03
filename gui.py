import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from image_processor import ImageProcessor

class ImageEditorGUI:
    """
    A Tkinter-based image editor that allows loading,
    cropping, resizing, applying filters, undo/redo, and saving images.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Image Editor")
        self.root.geometry("1000x700")
        
        # Optionally set a nicer ttk theme
        style = ttk.Style(self.root)
        # style.theme_use('clam')  # you can experiment with 'clam', 'default', etc.

        self.processor = ImageProcessor()
        self.photo = None  # Holds the current PhotoImage for display

        self.crop_start = None
        self.crop_rect = None

        self.setup_gui()
        self.setup_keyboard_shortcuts()

    def setup_gui(self):
        """
        Builds the GUI layout: menubar, toolbar, main frame, canvas, etc.
        """
        # Create a menu bar (File / Edit / Help)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.load_image)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Bonus: we could add a Help menu if desired
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Create a toolbar frame
        self.toolbar = ttk.Frame(self.root, padding=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Toolbar buttons
        ttk.Button(self.toolbar, text="Open", command=self.load_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Filter buttons
        ttk.Button(self.toolbar, text="Blur", command=lambda: self.apply_filter("blur")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Sharpen", command=lambda: self.apply_filter("sharpen")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Grayscale", command=lambda: self.apply_filter("grayscale")).pack(side=tk.LEFT, padx=2)

        # Another separator
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Resize slider
        ttk.Label(self.toolbar, text="Scale:").pack(side=tk.LEFT, padx=2)
        self.scale_var = tk.DoubleVar(value=100)
        self.scale = ttk.Scale(
            self.toolbar,
            from_=1,
            to=500,
            variable=self.scale_var,
            orient=tk.HORIZONTAL,
            command=self.on_scale
        )
        self.scale.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)

        # Scale label
        self.scale_label = ttk.Label(self.toolbar, text="100%")
        self.scale_label.pack(side=tk.LEFT, padx=5)

        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.main_frame, bg='gray90')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind mouse events to enable cropping
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

    def setup_keyboard_shortcuts(self):
        """
        Binds keyboard shortcuts to standard actions.
        """
        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def load_image(self):
        """
        Loads an image from the file dialog.
        """
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")])
        if not filepath:
            return  # user canceled
        # Attempt to load
        loaded_photo = self.processor.load_image(filepath)
        if loaded_photo is None:
            messagebox.showerror("Error", f"Failed to load image:\n{os.path.basename(filepath)}")
            return
        self.photo = loaded_photo
        self.display_image()

    def save_image(self):
        """
        Saves the current image to a user-selected path.
        """
        if self.photo is None:
            messagebox.showwarning("No Image", "No image to save. Please open or edit an image first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if not filepath:
            return  # user canceled

        if self.processor.save_image(filepath):
            messagebox.showinfo("Success", f"Image saved successfully:\n{os.path.basename(filepath)}")
        else:
            messagebox.showerror("Error", "Failed to save image. Check file path or permissions.")

    def display_image(self):
        """
        Clears the canvas and displays the current self.photo if available.
        """
        self.canvas.delete("all")
        if self.photo:
            # Make the canvas large enough for the image
            self.canvas.config(width=self.photo.width(), height=self.photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def start_crop(self, event):
        """
        Marks the initial point for cropping and creates a rectangle on the canvas.
        """
        if self.photo is None:
            return
        self.crop_start = (event.x, event.y)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red')

    def update_crop(self, event):
        """
        Resizes the cropping rectangle as the user drags the mouse.
        """
        if self.photo is None or not self.crop_rect or not self.crop_start:
            return
        self.canvas.coords(self.crop_rect, self.crop_start[0], self.crop_start[1], event.x, event.y)

    def end_crop(self, event):
        """
        Finalizes the crop operation, updates the displayed image with the cropped version.
        """
        if self.photo is None or not self.crop_rect or not self.crop_start:
            return

        x1, y1 = self.crop_start
        x2, y2 = event.x, event.y

        new_photo = self.processor.crop_image(x1, y1, x2, y2)
        # Clean up the rectangle
        self.canvas.delete(self.crop_rect)
        self.crop_rect = None
        self.crop_start = None

        if new_photo is None:
            # Possibly an invalid crop region
            messagebox.showwarning("Crop Error", "Invalid crop selection or no image loaded.")
            return

        self.photo = new_photo
        self.display_image()

    def on_scale(self, value):
        """
        Triggered when the user moves the resize slider; resizes the image in real-time.
        """
        if self.photo is None:
            return
        try:
            scale_value = float(value)
            self.scale_label.config(text=f"{int(scale_value)}%")
            new_photo = self.processor.resize_image(scale_value)
            if new_photo:
                self.photo = new_photo
                self.display_image()
        except ValueError:
            pass  # ignore invalid scale values

    def undo(self):
        """
        Undoes the last operation if possible.
        """
        if self.photo is None:
            return
        new_photo = self.processor.undo()
        if new_photo:
            self.photo = new_photo
            self.display_image()
        else:
            messagebox.showinfo("Undo", "Nothing to undo.")

    def redo(self):
        """
        Redoes a previously undone operation if possible.
        """
        if self.photo is None:
            return
        new_photo = self.processor.redo()
        if new_photo:
            self.photo = new_photo
            self.display_image()
        else:
            messagebox.showinfo("Redo", "Nothing to redo.")

    def apply_filter(self, filter_type):
        """
        Applies the selected filter (blur, sharpen, grayscale) to the image.
        """
        if self.photo is None:
            messagebox.showwarning("No Image", "Load an image before applying filters.")
            return
        new_photo = self.processor.apply_filter(filter_type)
        if new_photo:
            self.photo = new_photo
            self.display_image()

    def show_about(self):
        """
        Displays a simple 'About' dialog.
        """
        messagebox.showinfo("About", "Enhanced Image Editor\nCreated with Python, Tkinter & OpenCV.")

def main():
    root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
