"""
Main Hub Launcher
Central window to launch all features and demos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys

LAUNCH_ITEMS = [
    ("Interactive Simulation", "interactive_simulation.py", "🌌"),
    ("Educational Features & Quiz", "educational_quiz_gui.py", "📚"),
    ("Realistic Solar System Demo", "realistic_solar_system_demo.py", "🪐")
]

class MainHub:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Orbital Mechanics Simulator - Main Hub")
        self.root.geometry("700x500")
        
        self.create_ui()
    
    def create_ui(self):
        title = ttk.Label(self.root, text="Orbital Mechanics Simulator", font=("Arial", 20, "bold"))
        title.pack(pady=16)
        subtitle = ttk.Label(self.root, text="Choose a module to launch", font=("Arial", 11))
        subtitle.pack(pady=(0, 10))
        
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        for name, script, icon in LAUNCH_ITEMS:
            btn = ttk.Button(container, text=f"{icon}  {name}", command=lambda s=script: self.launch(s))
            btn.pack(fill=tk.X, pady=6)
        
        footer = ttk.Label(self.root, text="Tip: You can navigate between modules from the 'Hub' menu inside each window.")
        footer.pack(pady=(8, 0))
    
    def launch(self, script):
        try:
            subprocess.Popen([sys.executable, script])
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch {script}: {e}")


def main():
    root = tk.Tk()
    MainHub(root)
    root.mainloop()

if __name__ == "__main__":
    main()
