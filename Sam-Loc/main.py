# main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.gui import SamLocGUI

def main():
    gui = SamLocGUI()
    gui.run()

if __name__ == "__main__":
    main()