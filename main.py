from tkinterdnd2 import TkinterDnD
from image_editor import ImageEditor

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageEditor(root)
    root.mainloop() 