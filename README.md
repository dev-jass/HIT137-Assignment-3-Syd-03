# Image Editor

A simple yet powerful image editor built with Python and Tkinter. This application allows users to perform basic image editing operations with a user-friendly interface.

## Features

- **Image Loading**
  - Load images through file dialog
  - Drag and drop support
  - Supports multiple image formats (PNG, JPG, JPEG, BMP, TIFF, WEBP)

- **Basic Operations**
  - Crop images with visual selection
  - Resize images (10% to 200%)
  - Undo/Redo functionality
  - Reset to original state

- **Image Adjustments**
  - Brightness control (-100 to +100)
  - Contrast adjustment (0.5 to 2.0)
  - Blur effect (0 to 50)

- **File Operations**
  - Save edited images
  - Automatic modified filename suggestion
  - Multiple export formats

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Setup Options

#### Using Make (Recommended)
```bash
make install-and-run
```

#### Windows (Without Make)
```bash
run.bat
```

#### Unix/MacOS (Without Make)
```bash
chmod +x run.sh  # Make script executable (first time only)
./run.sh
```

### Manual Setup
1. Create virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **Load an Image**
   - Click "Load Image" button or
   - Drag and drop an image file

2. **Edit Image**
   - Use mouse to draw crop selection
   - Adjust sliders for brightness, contrast, and blur
   - Use resize slider to scale image

3. **Save Changes**
   - Click "Save Image" button
   - Choose save location and format
   - Modified filename will be suggested automatically

## Dependencies

- opencv-python: Image processing
- pillow: Image handling
- tkinterdnd2: Drag and drop support
- numpy: Numerical operations

## Project Structure

```
image-editor/
├── main.py              # Application entry point
├── image_editor.py      # Main editor class
├── image_processor.py   # Image processing operations
├── requirements.txt     # Project dependencies
├── Makefile            # Build automation
├── run.bat             # Windows runner
├── run.sh              # Unix runner
└── README.md           # Documentation
```

## Cleaning Up

To remove virtual environment and cleanup:
```bash
make clean
```