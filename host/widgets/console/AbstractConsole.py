from abc import ABC, abstractmethod
import tkinter as tk

class AbstractConsole(ABC, tk.Frame):
    @abstractmethod
    def __init__(self, master):
        super().__init__(master)