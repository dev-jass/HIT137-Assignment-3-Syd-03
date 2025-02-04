import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
from tkinterdnd2 import DND_FILES
from image_processor import ImageProcessor
import os

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("900x700")

        # Initialize state
        self.image = None
        self.original_image = None
        self.display_image = None
        self.history = []
        self.redo_stack = []
        self.start_x = self.start_y = self.rect_id = None
        
        # Initialize effect state
        self.current_effects = {
            'brightness': 0,
            'contrast': 1.0,
            'blur': 0,
            'scale': 100
        }
        
        self.create_ui()
        self.bind_shortcuts()

    def create_ui(self):
        # Control buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset", command=self.reset_all).pack(side=tk.LEFT, padx=5)

        # Create frame for side-by-side canvases
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Original image canvas (left side)
        self.original_canvas = tk.Canvas(canvas_frame, bg="gray")
        self.original_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.original_label = tk.Label(self.root, text="Original Image", bg="gray", fg="white")
        self.original_label.place(relx=0.25, rely=0.05, anchor="center")

        # Modified image canvas (right side)
        self.canvas = tk.Canvas(canvas_frame, bg="gray", cursor="cross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.modified_label = tk.Label(self.root, text="Modified Image", bg="gray", fg="white")
        self.modified_label.place(relx=0.75, rely=0.05, anchor="center")
        
        self.dnd_label = tk.Label(self.canvas, text="Drag and drop image here", bg="gray", fg="white")
        self.dnd_label.place(relx=0.5, rely=0.5, anchor="center")

        # Bind canvas events
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        # Create sliders
        self.create_sliders()

        # Enable drag and drop
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.handle_drop)

    def create_sliders(self):
        # Resize slider
        self.slider = tk.Scale(self.root, from_=10, to=200, orient=tk.HORIZONTAL,
                             label="Resize (%)", command=self.apply_effects)
        self.slider.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.slider.set(100)

        # Blur slider
        blur_frame = tk.Frame(self.root)
        blur_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Label(blur_frame, text="Blur:").pack(side=tk.LEFT, padx=5)
        self.blur_slider = tk.Scale(blur_frame, from_=0, to=50, orient=tk.HORIZONTAL,
                                  command=self.apply_effects)
        self.blur_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.blur_slider.set(0)

        # Brightness slider
        brightness_frame = tk.Frame(self.root)
        brightness_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Label(brightness_frame, text="Brightness:").pack(side=tk.LEFT, padx=5)
        self.brightness_slider = tk.Scale(brightness_frame, from_=-100, to=100,
                                        orient=tk.HORIZONTAL, command=self.apply_effects)
        self.brightness_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.brightness_slider.set(0)

        # Contrast slider
        contrast_frame = tk.Frame(self.root)
        contrast_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        tk.Label(contrast_frame, text="Contrast:").pack(side=tk.LEFT, padx=5)
        self.contrast_slider = tk.Scale(contrast_frame, from_=0.5, to=2.0,
                                      orient=tk.HORIZONTAL, command=self.apply_effects,
                                      resolution=0.1)
        self.contrast_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.contrast_slider.set(1.0)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
        )
        if not file_path:
            return
        
        try:
            # Store the original filename without extension
            self.original_filename = os.path.splitext(os.path.basename(file_path))[0]
            
            pil_image = Image.open(file_path)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            self.original_image = np.array(pil_image)
            self.image = self.original_image.copy()
            
            self.reset_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def save_image(self):
        if self.image is None:
            messagebox.showwarning("Warning", "No image to save!")
            return

        # Create default filename with original name
        default_filename = f"{getattr(self, 'original_filename', 'image')}-modified"
        
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            cv2.imwrite(file_path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")

    def update_display(self):
        if self.image is None:
            return
        
        # Remove drag and drop label if it exists
        if self.dnd_label:
            self.dnd_label.place_forget()
            self.dnd_label = None
        
        # Get canvas sizes
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Update modified image
        img_ratio = self.image.shape[1] / self.image.shape[0]
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            display_width = canvas_width
            display_height = int(canvas_width / img_ratio)
        else:
            display_height = canvas_height
            display_width = int(canvas_height * img_ratio)
        
        display_img = cv2.resize(self.image, (display_width, display_height),
                               interpolation=cv2.INTER_LANCZOS4)
        self.display_image = ImageTk.PhotoImage(Image.fromarray(display_img))
        
        # Update original image
        orig_ratio = self.original_image.shape[1] / self.original_image.shape[0]
        if orig_ratio > canvas_ratio:
            orig_width = canvas_width
            orig_height = int(canvas_width / orig_ratio)
        else:
            orig_height = canvas_height
            orig_width = int(canvas_height * orig_ratio)
        
        orig_display = cv2.resize(self.original_image, (orig_width, orig_height),
                                interpolation=cv2.INTER_LANCZOS4)
        self.display_original = ImageTk.PhotoImage(Image.fromarray(orig_display))
        
        # Display images
        self.canvas.delete("all")
        self.original_canvas.delete("all")
        
        x = (canvas_width - display_width) // 2
        y = (canvas_height - display_height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.display_image)
        
        x_orig = (canvas_width - orig_width) // 2
        y_orig = (canvas_height - orig_height) // 2
        self.original_canvas.create_image(x_orig, y_orig, anchor=tk.NW,
                                        image=self.display_original)

    def start_crop(self, event):
        if self.image is None:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_offset = (canvas_width - self.display_image.width()) // 2
        y_offset = (canvas_height - self.display_image.height()) // 2
        
        if (x_offset <= event.x <= x_offset + self.display_image.width() and 
            y_offset <= event.y <= y_offset + self.display_image.height()):
            self.start_x = event.x
            self.start_y = event.y
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline="#00ff00", width=2
            )

    def draw_crop(self, event):
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def end_crop(self, event):
        if self.image is None or not self.rect_id:
            return

        try:
            # Get crop coordinates
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x_offset = (canvas_width - self.display_image.width()) // 2
            y_offset = (canvas_height - self.display_image.height()) // 2
            
            x1 = max(0, min(self.start_x, event.x) - x_offset)
            y1 = max(0, min(self.start_y, event.y) - y_offset)
            x2 = min(self.display_image.width(), max(self.start_x, event.x) - x_offset)
            y2 = min(self.display_image.height(), max(self.start_y, event.y) - y_offset)
            
            # Convert to original image coordinates
            scale_x = self.image.shape[1] / self.display_image.width()
            scale_y = self.image.shape[0] / self.display_image.height()
            
            x1, y1, x2, y2 = [int(coord) for coord in [
                x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y
            ]]
            
            if x2 <= x1 or y2 <= y1:
                return
            
            # Perform crop
            self.image = ImageProcessor.crop_image(self.image, x1, y1, x2, y2)
            self.history = [self.image.copy()]
            self.redo_stack.clear()
            
            # Reapply current effects
            self.apply_effects()
            
        finally:
            # Clean up crop rectangle
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    def reset_all(self):
        """Reset everything to original state"""
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.history = [self.image.copy()]
            self.redo_stack.clear()
            
            # Reset all sliders
            self.slider.set(100)
            self.blur_slider.set(0)
            self.brightness_slider.set(0)
            self.contrast_slider.set(1.0)
            
            self.current_effects = {
                'brightness': 0,
                'contrast': 1.0,
                'blur': 0,
                'scale': 100
            }
            
            self.update_display()

    def handle_drop(self, event):
        file_path = event.data
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
            try:
                file_path = file_path.strip('{}').strip('"')
                pil_image = Image.open(file_path)
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                self.original_image = np.array(pil_image)
                self.image = self.original_image.copy()
                self.reset_all()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load dropped image: {str(e)}")
        else:
            messagebox.showerror("Error", "Please drop only image files")

    def undo(self):
        if len(self.history) > 1:
            current_state = self.history.pop()
            self.redo_stack.append(current_state)
            self.image = self.history[-1].copy()
            self.update_display()
        else:
            messagebox.showinfo("Undo", "No more actions to undo.")

    def redo(self):
        if self.redo_stack:
            current_state = self.redo_stack.pop()
            self.history.append(current_state)
            self.image = current_state.copy()
            self.update_display()
        else:
            messagebox.showinfo("Redo", "No actions to redo.")

    def cancel_crop(self, event=None):
        """Cancel the current crop operation"""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            self.start_x = None
            self.start_y = None

    def apply_effects(self, *args):
        """Apply all effects when any slider changes"""
        if self.image is None:
            return
            
        try:
            # Get current slider values
            self.current_effects.update({
                'brightness': int(self.brightness_slider.get()),
                'contrast': float(self.contrast_slider.get()),
                'blur': int(self.blur_slider.get()),
                'scale': int(self.slider.get())
            })
            
            # Start with original or cropped base image
            if len(self.history) > 0:
                base_image = self.history[0].copy()
            else:
                base_image = self.original_image.copy()
            
            # Apply all effects
            self.image = ImageProcessor.apply_effects(
                base_image,
                brightness=self.current_effects['brightness'],
                contrast=self.current_effects['contrast'],
                blur=self.current_effects['blur']
            )
            
            # Apply resize if needed
            if self.current_effects['scale'] != 100:
                self.image = ImageProcessor.resize_image(
                    self.image, 
                    self.current_effects['scale']
                )
            
            # Update history
            self.history.append(self.image.copy())
            self.redo_stack.clear()
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply effects: {str(e)}")

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-Shift-Z>', lambda e: self.redo())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-o>', lambda e: self.load_image())
        self.root.bind('<Escape>', self.cancel_crop)

    # ... (rest of the existing methods, but update slider callbacks to use apply_effects) ... 