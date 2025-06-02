# -*- coding: utf-8 -*-
# main.py

import tkinter as tk
from ui import FileIntegrityGUI

def main():
    root = tk.Tk()
    app = FileIntegrityGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
