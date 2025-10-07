"""
educational features for orbital mechanics simulator
learning tools and educational content
"""

from orbital_simulator import OrbitalSimulator, CelestialBody, SUN_MASS, EARTH_MASS, AU
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import tkinter as tk
from tkinter import ttk, messagebox
import json

class EducationalFeatures:
    def __init__(self):
        self.planet_facts = self.load_planet_facts()
        self.quiz_questions = self.load_quiz_questions()
        
    def load_planet_facts(self):
        """Load educational facts about planets"""
        return {
            "Sun": {
                "type": "Star",
                "mass": "1.989 × 10³⁰ kg",
                "temperature": "5,778 K",
                "composition": "73% Hydrogen, 25% Helium",
                "age": "4.6 billion years",
                "fun_fact": "The Sun contains 99.86% of the solar system's mass!"
            },
            "Mercury": {
                "type": "Terrestrial Planet",
                "distance": "0.39 AU",
                "period": "88 Earth days",
                "surface": "Rocky, heavily cratered",
                "atmosphere": "Very thin",
                "fun_fact": "Mercury has the most eccentric orbit of all planets!"
            },
            "Venus": {
                "type": "Terrestrial Planet", 
                "distance": "0.72 AU",
                "period": "225 Earth days",
                "surface": "Volcanic, hot",
                "atmosphere": "96.5% CO₂, thick clouds",
                "fun_fact": "Venus rotates backwards - a day is longer than a year!"
            },
            "Earth": {
                "type": "Terrestrial Planet",
                "distance": "1.0 AU", 
                "period": "365.25 days",
                "surface": "71% water, 29% land",
                "atmosphere": "78% N₂, 21% O₂",
                "fun_fact": "Earth is the only known planet with life!"
            },
            "Mars": {
                "type": "Terrestrial Planet",
                "distance": "1.52 AU",
                "period": "687 Earth days", 
                "surface": "Red dust, polar ice caps",
                "atmosphere": "95% CO₂, very thin",
                "fun_fact": "Mars has the largest volcano in the solar system - Olympus Mons!"
            },
            "Jupiter": {
                "type": "Gas Giant",
                "distance": "5.2 AU",
                "period": "12 Earth years",
                "surface": "Gas layers, no solid surface",
                "atmosphere": "89% H₂, 10% He",
                "fun_fact": "Jupiter's Great Red Spot is a storm larger than Earth!"
            },
            "Saturn": {
                "type": "Gas Giant",
                "distance": "9.58 AU", 
                "period": "29 Earth years",
                "surface": "Gas layers, no solid surface",
                "atmosphere": "96% H₂, 3% He",
                "fun_fact": "Saturn is less dense than water - it would float!"
            },
            "Uranus": {
                "type": "Ice Giant",
                "distance": "19.2 AU",
                "period": "84 Earth years",
                "surface": "Ice and gas layers",
                "atmosphere": "83% H₂, 15% He, 2% CH₄",
                "fun_fact": "Uranus rotates on its side - it's tilted 98 degrees!"
            },
            "Neptune": {
                "type": "Ice Giant", 
                "distance": "30.1 AU",
                "period": "165 Earth years",
                "surface": "Ice and gas layers",
                "atmosphere": "80% H₂, 19% He, 1% CH₄",
                "fun_fact": "Neptune has the strongest winds in the solar system - up to 2,100 km/h!"
            }
        }
    
    def load_quiz_questions(self):
        """Load quiz questions for learning"""
        return [
            {
                "question": "Which planet is closest to the Sun?",
                "options": ["Venus", "Mercury", "Earth", "Mars"],
                "correct": 1,
                "explanation": "Mercury is the closest planet to the Sun at 0.39 AU."
            },
            {
                "question": "What is the largest planet in our solar system?",
                "options": ["Saturn", "Jupiter", "Neptune", "Earth"],
                "correct": 1,
                "explanation": "Jupiter is the largest planet, containing more mass than all other planets combined."
            },
            {
                "question": "Which planet has the most eccentric orbit?",
                "options": ["Earth", "Mars", "Mercury", "Venus"],
                "correct": 2,
                "explanation": "Mercury has the most eccentric (elliptical) orbit of all planets."
            },
            {
                "question": "What is the Great Red Spot?",
                "options": ["A volcano on Mars", "A storm on Jupiter", "A crater on Mercury", "A cloud on Venus"],
                "correct": 1,
                "explanation": "The Great Red Spot is a giant storm on Jupiter that has been raging for centuries."
            },
            {
                "question": "Which planet is known as the 'Red Planet'?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": 1,
                "explanation": "Mars is called the 'Red Planet' due to iron oxide (rust) on its surface."
            }
        ]
    
    def show_planet_info(self, planet_name):
        """Display detailed information about a planet"""
        if planet_name not in self.planet_facts:
            return f"Information about {planet_name} not available."
        
        facts = self.planet_facts[planet_name]
        info = f"🪐 {planet_name} Information\n\n"
        
        for key, value in facts.items():
            if key == "fun_fact":
                info += f"🌟 Fun Fact: {value}\n"
            else:
                info += f"• {key.replace('_', ' ').title()}: {value}\n"
        
        return info
    
    def create_learning_scenarios(self):
        """Create educational scenarios for learning"""
        scenarios = {
            "Kepler's Laws": self.create_keplers_laws_demo(),
            "Orbital Mechanics": self.create_orbital_mechanics_demo(),
            "Planet Comparison": self.create_planet_comparison_demo(),
            "Gravitational Forces": self.create_gravity_demo()
        }
        return scenarios
    
    def create_keplers_laws_demo(self):
        """Demonstrate Kepler's laws of planetary motion"""
        print("📚 Kepler's Laws Demonstration")
        print("=" * 35)
        
        simulator = OrbitalSimulator([], dt=3600.0)
        
        sun = CelestialBody("Sun", SUN_MASS, [0, 0, 0], [0, 0, 0], 20, '#FFD700', is_3d=True)
        
        planet = CelestialBody("Planet", EARTH_MASS, [2 * AU, 0, 0], 
                              [0, 20000, 0], 6, '#4169E1', is_3d=True)
        
        simulator.physics_engine.bodies = [sun, planet]
        simulator.trajectories = {body.name: [] for body in simulator.physics_engine.bodies}
        
        print("Kepler's Laws:")
        print("1. Law of Ellipses: Planets orbit in elliptical paths")
        print("2. Law of Equal Areas: Planets sweep equal areas in equal times")
        print("3. Law of Harmonies: T² ∝ a³ (period squared ∝ semi-major axis cubed)")
        
        simulator.run_simulation(365 * 24 * 3600)
        
        fig, ax = simulator.visualize(use_3d=True, realistic_space=True)
        ax.set_title("📚 Kepler's Laws - Elliptical Orbit", color='white', fontsize=14)
        plt.show()
        
        return simulator
    
    def create_orbital_mechanics_demo(self):
        """Demonstrate orbital mechanics concepts"""
        print("\n🚀 Orbital Mechanics Demonstration")
        print("=" * 40)
        
        simulator = OrbitalSimulator([], dt=1800.0)
        
        star = CelestialBody("Star", SUN_MASS, [0, 0, 0], [0, 0, 0], 15, '#FFD700', is_3d=True)
        
        circular_orbit = CelestialBody("Circular Orbit", EARTH_MASS, [AU, 0, 0], 
                                      [0, 29780, 0], 4, '#4169E1', is_3d=True)
        
        elliptical_orbit = CelestialBody("Elliptical Orbit", EARTH_MASS, [1.5 * AU, 0, 0], 
                                        [0, 20000, 0], 4, '#CD5C5C', is_3d=True)
        
        inclined_orbit = CelestialBody("Inclined Orbit", EARTH_MASS, [2 * AU, 0, 0.5 * AU], 
                                      [0, 15000, 5000], 4, '#32CD32', is_3d=True)
        
        simulator.physics_engine.bodies = [star, circular_orbit, elliptical_orbit, inclined_orbit]
        simulator.trajectories = {body.name: [] for body in simulator.physics_engine.bodies}
        
        print("Orbital Mechanics Concepts:")
        print("• Circular orbits: Constant distance, constant speed")
        print("• Elliptical orbits: Varying distance, varying speed")
        print("• Inclined orbits: 3D motion, orbital plane tilt")
        
        simulator.run_simulation(180 * 24 * 3600) 
        
        fig, ax = simulator.visualize(use_3d=True, realistic_space=True)
        ax.set_title("🚀 Orbital Mechanics - Different Orbit Types", color='white', fontsize=14)
        plt.show()
        
        return simulator
    
    def create_planet_comparison_demo(self):
        """Create planet comparison visualization"""
        print("\n📊 Planet Comparison")
        print("=" * 25)
        
        planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        distances = [0.39, 0.72, 1.0, 1.52, 5.2, 9.58, 19.2, 30.1]
        sizes = [0.38, 0.95, 1.0, 0.53, 11.2, 9.4, 4.0, 3.9]
        colors = ['#8C7853', '#FF8C00', '#4169E1', '#CD5C5C', '#D2691E', '#F4A460', '#4FD0E7', '#4169E1']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='black')
        
        ax1.bar(planets, distances, color=colors)
        ax1.set_ylabel('Distance from Sun (AU)', color='white')
        ax1.set_title('Planet Distances from Sun', color='white', fontsize=14)
        ax1.tick_params(colors='white')
        ax1.set_facecolor('black')
        
        ax2.bar(planets, sizes, color=colors)
        ax2.set_ylabel('Relative Size (Earth = 1)', color='white')
        ax2.set_title('Planet Sizes (Relative to Earth)', color='white', fontsize=14)
        ax2.tick_params(colors='white')
        ax2.set_facecolor('black')
        
        plt.tight_layout()
        plt.show()
        
        return planets, distances, sizes
    
    def create_gravity_demo(self):
        """Demonstrate gravitational forces"""
        print("\n⚡ Gravitational Forces Demonstration")
        print("=" * 45)
        
        simulator = OrbitalSimulator([], dt=3600.0)
        
        body1 = CelestialBody("Body 1", SUN_MASS, [-0.5 * AU, 0, 0], [0, 0, 0], 10, '#FFD700', is_3d=True)
        body2 = CelestialBody("Body 2", SUN_MASS * 0.5, [0.5 * AU, 0, 0], [0, 0, 0], 8, '#4169E1', is_3d=True)
        
        simulator.physics_engine.bodies = [body1, body2]
        simulator.trajectories = {body.name: [] for body in simulator.physics_engine.bodies}
        
        print("Gravitational Forces:")
        print("• F = G × m₁ × m₂ / r²")
        print("• Force increases with mass")
        print("• Force decreases with distance squared")
        print("• Bodies orbit around common center of mass")
        
        simulator.run_simulation(90 * 24 * 3600)  # 3 months
        
        fig, ax = simulator.visualize(use_3d=True, realistic_space=True)
        ax.set_title("⚡ Gravitational Forces - Binary System", color='white', fontsize=14)
        plt.show()
        
        return simulator
    
    def run_quiz(self):
        """Run an educational quiz"""
        print("\n🧠 Quiz")
        print("=" * 30)
        
        score = 0
        total = len(self.quiz_questions)
        
        for i, question in enumerate(self.quiz_questions):
            print(f"\nQuestion {i+1}/{total}: {question['question']}")
            for j, option in enumerate(question['options']):
                print(f"  {j+1}. {option}")
            
            while True:
                try:
                    answer = int(input("Your answer (1-4): ")) - 1
                    if 0 <= answer <= 3:
                        break
                    else:
                        print("Please enter 1, 2, 3, or 4")
                except ValueError:
                    print("Please enter a number")
            
            if answer == question['correct']:
                print("✅ Correct!")
                score += 1
            else:
                print("❌ Incorrect!")
            
            print(f"Explanation: {question['explanation']}")
        
        print(f"\n🎯 Quiz Results: {score}/{total} ({score/total*100:.1f}%)")
        
        if score == total:
            print("🌟 Well... Questions were easy... so, meh.")
        elif score >= total * 0.8:
            print("🎉 Great job, buddy.")
        elif score >= total * 0.6:
            print("👍 Not bad, average astronomy knowledge.")
        else:
            print("📚 Embarrasing. You don't know the Solar System you are living in?.. You need help, and you are in the right place for it.")
        
        return score, total

def main():
    """Main function to run educational features"""
    print("📚 Educational Features Demo")
    print("=" * 30)
    
    edu = EducationalFeatures()
    
    #planet info
    print("\n🪐 Planet Information:")
    for planet in ["Earth", "Mars", "Jupiter"]:
        print(edu.show_planet_info(planet))
        print("-" * 40)
    
    #learning scenarios
    print("\n📚 Learning Scenarios:")
    scenarios = edu.create_learning_scenarios()
    
    print("\n🧠 Educational Quiz:")
    edu.run_quiz()
    
    print("\n🎉 Educational features demo completed!")
    print("\nFeatures demonstrated:")
    print("✓ Planet information and facts")
    print("✓ Kepler's laws demonstration")
    print("✓ Orbital mechanics concepts")
    print("✓ Planet comparison charts")
    print("✓ Gravitational forces demo")
    print("✓ Interactive quiz system")

if __name__ == "__main__":
    main()