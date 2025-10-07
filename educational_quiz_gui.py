"""
Educational Quiz GUI
Interactive quiz system with GUI for the orbital mechanics simulator
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from orbital_simulator import OrbitalSimulator, CelestialBody, SUN_MASS, EARTH_MASS, AU, G

class EducationalQuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Orbital Mechanics Quiz - Educational Edition")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
 
        self.current_question = 0
        self.score = 0
        self.total_questions = 0
        self.quiz_questions = self.load_quiz_questions()
        self.user_answers = []
        
        # Create GUI
        self.create_widgets()
        self.start_quiz()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Top menu to navigate across app sections
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        hub_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hub", menu=hub_menu)
        hub_menu.add_command(label="Open Main Hub", command=self.open_main_hub)
        hub_menu.add_separator()
        hub_menu.add_command(label="Interactive Simulation", command=self.open_simulator)
        hub_menu.add_command(label="Educational Features", command=lambda: None)
        hub_menu.add_command(label="Planet Data Analyzer", command=self.open_planet_analyzer)
        hub_menu.add_command(label="Professional Features", command=self.open_professional_features)

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="🧠 Orbital Mechanics Quiz", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_label = ttk.Label(progress_frame, text="Question 1 of 5", 
                                      font=('Arial', 12))
        self.progress_label.pack(side=tk.LEFT)
        
        self.score_label = ttk.Label(progress_frame, text="Score: 0/5", 
                                    font=('Arial', 12))
        self.score_label.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 20))
        
        # Question frame
        self.question_frame = ttk.LabelFrame(main_frame, text="Question", padding=20)
        self.question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Question text
        self.question_label = ttk.Label(self.question_frame, text="", 
                                       font=('Arial', 14), wraplength=800)
        self.question_label.pack(pady=(0, 20))
        
        # Answer options frame
        self.options_frame = ttk.Frame(self.question_frame)
        self.options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Answer variable
        self.answer_var = tk.StringVar()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.prev_button = ttk.Button(button_frame, text="← Previous", 
                                     command=self.previous_question, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_button = ttk.Button(button_frame, text="Next →", 
                                     command=self.next_question)
        self.next_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.submit_button = ttk.Button(button_frame, text="Submit Quiz", 
                                       command=self.submit_quiz, state=tk.DISABLED)
        self.submit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.restart_button = ttk.Button(button_frame, text="🔄 Restart", 
                                        command=self.restart_quiz)
        self.restart_button.pack(side=tk.RIGHT)
        
        # Results frame (hidden initially)
        self.results_frame = ttk.LabelFrame(main_frame, text="Quiz Results", padding=20)
        
        self.results_text = tk.Text(self.results_frame, height=15, width=80, wrap=tk.WORD, 
                                   bg='#2a2a2a', fg='white', font=('Arial', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Results frame initially hidden
        self.results_frame.pack_forget()
        
    def load_quiz_questions(self):
        """Load quiz questions with enhanced content"""
        return [
            {
                "question": "Which planet is closest to the Sun?",
                "options": ["Venus", "Mercury", "Earth", "Mars"],
                "correct": 1,
                "explanation": "Mercury is the closest planet to the Sun at 0.39 AU. It's also the smallest planet in our solar system.",
                "image": "mercury_orbit"
            },
            {
                "question": "What is the largest planet in our solar system?",
                "options": ["Saturn", "Jupiter", "Neptune", "Earth"],
                "correct": 1,
                "explanation": "Jupiter is the largest planet, containing more mass than all other planets combined. It's a gas giant with a Great Red Spot storm.",
                "image": "jupiter_features"
            },
            {
                "question": "Which planet has the most eccentric (elliptical) orbit?",
                "options": ["Earth", "Mars", "Mercury", "Venus"],
                "correct": 2,
                "explanation": "Mercury has the most eccentric orbit of all planets, ranging from 0.31 to 0.47 AU from the Sun.",
                "image": "mercury_eccentric"
            },
            {
                "question": "What is the Great Red Spot?",
                "options": ["A volcano on Mars", "A storm on Jupiter", "A crater on Mercury", "A cloud on Venus"],
                "correct": 1,
                "explanation": "The Great Red Spot is a giant storm on Jupiter that has been raging for centuries. It's larger than Earth!",
                "image": "jupiter_red_spot"
            },
            {
                "question": "Which planet is known as the 'Red Planet'?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": 1,
                "explanation": "Mars is called the 'Red Planet' due to iron oxide (rust) on its surface, giving it a reddish appearance.",
                "image": "mars_surface"
            },
            {
                "question": "What causes the seasons on Earth?",
                "options": ["Earth's distance from the Sun", "Earth's axial tilt", "Earth's rotation speed", "Earth's magnetic field"],
                "correct": 1,
                "explanation": "Earth's axial tilt of 23.5 degrees causes the seasons. When one hemisphere tilts toward the Sun, it's summer there.",
                "image": "earth_seasons"
            },
            {
                "question": "Which planet has the strongest winds in the solar system?",
                "options": ["Jupiter", "Saturn", "Uranus", "Neptune"],
                "correct": 3,
                "explanation": "Neptune has the strongest winds in the solar system, reaching speeds up to 2,100 km/h (1,300 mph).",
                "image": "neptune_winds"
            },
            {
                "question": "What are Saturn's rings made of?",
                "options": ["Solid rock", "Ice and rock particles", "Gas", "Dust only"],
                "correct": 1,
                "explanation": "Saturn's rings are made of ice and rock particles ranging from tiny grains to house-sized chunks.",
                "image": "saturn_rings"
            }
        ]
    
    def start_quiz(self):
        """Start the quiz"""
        self.total_questions = len(self.quiz_questions)
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.show_question()
        
    def show_question(self):
        """Show the current question"""
        if self.current_question >= self.total_questions:
            return
            
        question_data = self.quiz_questions[self.current_question]
        
        # Update progress
        self.progress_label.config(text=f"Question {self.current_question + 1} of {self.total_questions}")
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}")
        self.progress_bar['value'] = (self.current_question / self.total_questions) * 100
        
        # Show question
        self.question_label.config(text=question_data['question'])
        
        # Clear previous options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # Create radio buttons for options
        for i, option in enumerate(question_data['options']):
            ttk.Radiobutton(self.options_frame, text=option, variable=self.answer_var, 
                           value=str(i), command=self.on_answer_selected).pack(anchor=tk.W, pady=2)
        
        # Update buttons
        self.prev_button.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        
        if self.current_question == self.total_questions - 1:
            self.next_button.config(text="Finish Quiz")
            self.submit_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(text="Next →")
            self.submit_button.config(state=tk.DISABLED)
        
        # Clear selection
        self.answer_var.set("")
        
    def on_answer_selected(self):
        """Handle answer selection"""
        # Store the answer
        if len(self.user_answers) <= self.current_question:
            self.user_answers.extend([None] * (self.current_question + 1 - len(self.user_answers)))
        
        self.user_answers[self.current_question] = int(self.answer_var.get())
        
        # Check if answer is correct
        question_data = self.quiz_questions[self.current_question]
        if self.user_answers[self.current_question] == question_data['correct']:
            if self.current_question not in [i for i, ans in enumerate(self.user_answers) if ans is not None]:
                self.score += 1
        
    def previous_question(self):
        """Go to previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()
    
    def next_question(self):
        """Go to next question"""
        if self.current_question < self.total_questions - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.submit_quiz()
    
    def submit_quiz(self):
        """Submit the quiz and show results"""
        # Calculate final score
        final_score = 0
        for i, answer in enumerate(self.user_answers):
            if answer == self.quiz_questions[i]['correct']:
                final_score += 1
        
        self.score = final_score
        
        # Hide question frame and show results
        self.question_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Generate results
        self.generate_results()
        
    def generate_results(self):
        """Generate and display quiz results"""
        results_text = f"🎯 QUIZ RESULTS\n"
        results_text += f"{'='*50}\n\n"
        
        # Score summary
        percentage = (self.score / self.total_questions) * 100
        results_text += f"Final Score: {self.score}/{self.total_questions} ({percentage:.1f}%)\n\n"
        
        # Performance message
        if percentage == 100:
            results_text += "🌟 PERFECT! You're an orbital mechanics expert!\n\n"
        elif percentage >= 80:
            results_text += "🎉 Excellent! You know your planets very well!\n\n"
        elif percentage >= 60:
            results_text += "👍 Good work! Keep learning about space!\n\n"
        else:
            results_text += "📚 Keep studying! The universe is full of wonders!\n\n"
        
        # Detailed results
        results_text += "📋 DETAILED RESULTS\n"
        results_text += f"{'='*30}\n\n"
        
        for i, question_data in enumerate(self.quiz_questions):
            user_answer = self.user_answers[i] if i < len(self.user_answers) else None
            is_correct = user_answer == question_data['correct']
            
            results_text += f"Question {i+1}: {'✅' if is_correct else '❌'}\n"
            results_text += f"Q: {question_data['question']}\n"
            
            if user_answer is not None:
                results_text += f"Your answer: {question_data['options'][user_answer]}\n"
            else:
                results_text += f"Your answer: (No answer)\n"
            
            results_text += f"Correct answer: {question_data['options'][question_data['correct']]}\n"
            results_text += f"Explanation: {question_data['explanation']}\n\n"
        
        # Learning tips
        results_text += "💡 LEARNING TIPS\n"
        results_text += f"{'='*20}\n\n"
        results_text += "• Try the interactive solar system simulator\n"
        results_text += "• Explore different planet scenarios\n"
        results_text += "• Use the educational features to learn more\n"
        results_text += "• Practice with different quiz questions\n"
        results_text += "• Watch the realistic planet animations\n\n"
        
        results_text += "🚀 Keep exploring the cosmos!"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results_text)
        
    def restart_quiz(self):
        """Restart the quiz"""
        # Hide results and show questions
        self.results_frame.pack_forget()
        self.question_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Reset quiz
        self.start_quiz()

class EducationalFeaturesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Educational Features - Orbital Mechanics")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the main educational GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="📚 Educational Features", 
                              font=('Arial', 24, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Feature buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Quiz button
        quiz_button = ttk.Button(button_frame, text="🧠 Take Quiz", 
                                command=self.open_quiz, width=20)
        quiz_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Planet info button
        info_button = ttk.Button(button_frame, text="🪐 Planet Information", 
                                command=self.show_planet_info, width=20)
        info_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Learning scenarios button
        scenarios_button = ttk.Button(button_frame, text="📚 Learning Scenarios", 
                                     command=self.show_learning_scenarios, width=20)
        scenarios_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Interactive simulator button
        simulator_button = ttk.Button(button_frame, text="🌌 Interactive Simulator", 
                                     command=self.open_simulator, width=20)
        simulator_button.pack(side=tk.LEFT)
        
        # Content area
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show welcome message
        self.show_welcome()
        
    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """
🌌 Welcome to the Educational Features!

This interactive learning system helps you explore orbital mechanics through:

🧠 Interactive Quiz
• Test your knowledge of planets and orbital mechanics
• Get detailed explanations for each answer
• Track your progress and improve your score

🪐 Planet Information
• Learn fascinating facts about each planet
• Discover unique characteristics and features
• Explore the solar system in detail

📚 Learning Scenarios
• Visual demonstrations of Kepler's laws
• Interactive orbital mechanics examples
• Educational simulations and comparisons

🌌 Interactive Simulator
• Real-time orbital mechanics simulation
• Realistic planet appearances
• 3D visualization with zoom and rotation

Click any button above to start learning!
        """
        
        welcome_label = ttk.Label(self.content_frame, text=welcome_text, 
                                 font=('Arial', 12), justify=tk.LEFT)
        welcome_label.pack(pady=50)
        
    def open_quiz(self):
        """Open the quiz window"""
        quiz_window = tk.Toplevel(self.root)
        quiz_window.title("🧠 Orbital Mechanics Quiz")
        quiz_window.geometry("1000x700")
        quiz_window.configure(bg='#1a1a1a')
        
        EducationalQuizGUI(quiz_window)
        
    def show_planet_info(self):
        """Show planet information"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create planet info display
        info_text = """
🪐 PLANET INFORMATION

☀️ SUN
• Type: Star
• Mass: 1.989 × 10³⁰ kg
• Temperature: 5,778 K
• Composition: 73% Hydrogen, 25% Helium
• Age: 4.6 billion years
• Fun Fact: The Sun contains 99.86% of the solar system's mass!

🪐 MERCURY
• Type: Terrestrial Planet
• Distance: 0.39 AU
• Period: 88 Earth days
• Surface: Rocky, heavily cratered
• Atmosphere: Very thin
• Fun Fact: Mercury has the most eccentric orbit of all planets!

🪐 VENUS
• Type: Terrestrial Planet
• Distance: 0.72 AU
• Period: 225 Earth days
• Surface: Volcanic, hot
• Atmosphere: 96.5% CO₂, thick clouds
• Fun Fact: Venus rotates backwards - a day is longer than a year!

🌍 EARTH
• Type: Terrestrial Planet
• Distance: 1.0 AU
• Period: 365.25 days
• Surface: 71% water, 29% land
• Atmosphere: 78% N₂, 21% O₂
• Fun Fact: Earth is the only known planet with life!

🪐 MARS
• Type: Terrestrial Planet
• Distance: 1.52 AU
• Period: 687 Earth days
• Surface: Red dust, polar ice caps
• Atmosphere: 95% CO₂, very thin
• Fun Fact: Mars has the largest volcano in the solar system - Olympus Mons!

🪐 JUPITER
• Type: Gas Giant
• Distance: 5.2 AU
• Period: 12 Earth years
• Surface: Gas layers, no solid surface
• Atmosphere: 89% H₂, 10% He
• Fun Fact: Jupiter's Great Red Spot is a storm larger than Earth!

🪐 SATURN
• Type: Gas Giant
• Distance: 9.58 AU
• Period: 29 Earth years
• Surface: Gas layers, no solid surface
• Atmosphere: 96% H₂, 3% He
• Fun Fact: Saturn is less dense than water - it would float!

🪐 URANUS
• Type: Ice Giant
• Distance: 19.2 AU
• Period: 84 Earth years
• Surface: Ice and gas layers
• Atmosphere: 83% H₂, 15% He, 2% CH₄
• Fun Fact: Uranus rotates on its side - it's tilted 98 degrees!

🪐 NEPTUNE
• Type: Ice Giant
• Distance: 30.1 AU
• Period: 165 Earth years
• Surface: Ice and gas layers
• Atmosphere: 80% H₂, 19% He, 1% CH₄
• Fun Fact: Neptune has the strongest winds in the solar system - up to 2,100 km/h!
        """
        
        info_label = ttk.Label(self.content_frame, text=info_text, 
                              font=('Arial', 10), justify=tk.LEFT)
        info_label.pack(pady=20)
        
    def show_learning_scenarios(self):
        """Show learning scenarios"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        scenarios_text = """
📚 LEARNING SCENARIOS

🔬 Kepler's Laws Demonstration
• Law of Ellipses: Planets orbit in elliptical paths
• Law of Equal Areas: Planets sweep equal areas in equal times
• Law of Harmonies: T² ∝ a³ (period squared ∝ semi-major axis cubed)

🚀 Orbital Mechanics Concepts
• Circular orbits: Constant distance, constant speed
• Elliptical orbits: Varying distance, varying speed
• Inclined orbits: 3D motion, orbital plane tilt

⚡ Gravitational Forces
• F = G × m₁ × m₂ / r²
• Force increases with mass
• Force decreases with distance squared
• Bodies orbit around common center of mass

📊 Planet Comparisons
• Size comparisons relative to Earth
• Distance comparisons from the Sun
• Speed comparisons in orbital motion
• Mass comparisons across the solar system

🌍 Earth's Seasons
• Caused by Earth's axial tilt of 23.5°
• When one hemisphere tilts toward Sun = summer
• Opposite hemisphere = winter
• Spring and autumn during transitions

💫 Moon Phases
• Caused by Moon's position relative to Earth and Sun
• New Moon: Moon between Earth and Sun
• Full Moon: Earth between Moon and Sun
• Quarter phases: 90° angles

Click "Interactive Simulator" to see these concepts in action!
        """
        
        scenarios_label = ttk.Label(self.content_frame, text=scenarios_text, 
                                   font=('Arial', 10), justify=tk.LEFT)
        scenarios_label.pack(pady=20)
        
    def open_simulator(self):
        """Open the interactive simulator"""
        try:
            subprocess.Popen([sys.executable, "interactive_simulation.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open simulator: {str(e)}")

    def open_main_hub(self):
        try:
            subprocess.Popen([sys.executable, "main_hub.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Main Hub: {e}")

    def open_planet_analyzer(self):
        try:
            subprocess.Popen([sys.executable, "planet_data_analyzer.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Planet Data Analyzer: {e}")

    def open_professional_features(self):
        try:
            subprocess.Popen([sys.executable, "professional_features.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Professional Features: {e}")

def main():
    """Main function to run the educational features"""
    root = tk.Tk()
    app = EducationalFeaturesGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
