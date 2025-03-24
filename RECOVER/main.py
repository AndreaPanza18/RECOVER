"""
The main entry point for launching the application.
"""

from RECOVER.gui.main_window import MainWindow

def main():
    """
    Main function to launch the CustomTkinter application.
    """
    app = MainWindow()  # Instantiate your main window
    app.mainloop()      # Start the GUI event loop

if __name__ == "__main__":
    main()
