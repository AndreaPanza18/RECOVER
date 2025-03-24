"""
This module defines the main window for the application using CustomTkinter.
"""

import customtkinter as ctk
from ..ml.model_logic import load_model, run_inference  # Example usage of your ML module

class MainWindow(ctk.CTk):
    """
    The main application window using CustomTkinter.
    """

    def __init__(self):
        """
        Initialize the main window and its widgets.
        """
        super().__init__()

        # Window configuration
        self.title("RECOVER")
        self.geometry("1600x900")

        # Set appearance/theme for CustomTkinter
        ctk.set_appearance_mode("system")  # "System", "Light", or "Dark"
        ctk.set_default_color_theme("blue")  # "blue", "green", or "dark-blue"

        # Optional: Load your ML model at startup
        self.model = load_model()  # Hypothetical function

        # Create UI elements
        self._create_widgets()

    def _create_widgets(self):
        """
        Create and place the widgets for the main window.
        """
        # Title label
        title_label = ctk.CTkLabel(
            master=self,
            text="Welcome to RECOVER",
            font=("Helvetica", 20)
        )
        title_label.pack(pady=20)

        # Entry field
        self.input_entry = ctk.CTkTextbox(
            master=self,
            height=300,
            width=500
        )
        self.input_entry.pack(pady=10)

        # Button to run inference
        run_button = ctk.CTkButton(
            master=self,
            text="Run Model",
            command=self._on_run_model
        )
        run_button.pack(pady=10)

        # Output label
        self.output_label = ctk.CTkLabel(
            master=self,
            text="RECOVER output will appear here.",
            font=("Helvetica", 14)
        )
        self.output_label.pack(pady=10)

    def _on_run_model(self):
        """
        Event handler for the 'Run Model' button.
        Retrieves user input, runs the model, and updates output_label.
        """
        user_input = self.input_entry.get('1.0', 'end-1c')

        # Example: run inference on user input
        result = run_inference(self.model, user_input)

        # Update the output label
        self.output_label.configure(text=f"{result}")
