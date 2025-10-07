"""
Realistic Solar System Demo
Complete solar system with all planets and realistic appearances
"""

from orbital_simulator import OrbitalSimulator, CelestialBody, SUN_MASS, EARTH_MASS, AU
import numpy as np
import matplotlib.pyplot as plt

def complete_solar_system():
    """Complete solar system with all planets and realistic appearances"""
    print("🌌 Complete Realistic Solar System")
    print("=" * 40)
    
    # Create simulator with complete solar system
    simulator = OrbitalSimulator([], dt=3600.0)  # 1 hour time step
    simulator.create_realistic_space_scene()
    
    print(f"Created complete solar system with {len(simulator.physics_engine.bodies)} bodies:")
    for body in simulator.physics_engine.bodies:
        print(f"  - {body.name}: {body.color}, Radius = {body.radius}")
    
    # Run simulation for 30 days
    print("\nRunning 30-day simulation...")
    simulator.run_simulation(30 * 24 * 3600)
    
    # Create realistic visualization
    print("Creating realistic solar system visualization...")
    print("Features:")
    print("  - Realistic planet surfaces")
    print("  - Earth with continents and atmosphere")
    print("  - Mars with polar ice caps")
    print("  - Jupiter with Great Red Spot")
    print("  - Saturn with rings")
    print("  - All planets with unique appearances")
    
    fig, ax = simulator.visualize(use_3d=True, realistic_space=True, interactive=True)
    plt.show()

def close_up_planets():
    """Show planets in close-up view for detailed examination"""
    print("\n🔍 Close-up Planet Views")
    print("=" * 30)
    
    # Create individual planet systems for close-up views
    planets_to_show = [
        ("Earth", EARTH_MASS, 8, '#4169E1'),
        ("Mars", EARTH_MASS * 0.107, 6, '#CD5C5C'),
        ("Jupiter", EARTH_MASS * 317.8, 20, '#D2691E'),
        ("Saturn", EARTH_MASS * 95.2, 18, '#F4A460')
    ]
    
    for planet_name, mass, radius, color in planets_to_show:
        print(f"\nShowing {planet_name} close-up...")
        
        # Create system with just the planet and sun
        sun = CelestialBody("Sun", SUN_MASS, [0, 0, 0], [0, 0, 0], 15, '#FFD700', is_3d=True)
        planet = CelestialBody(planet_name, mass, [2 * AU, 0, 0], [0, 30000, 0], radius, color, is_3d=True)
        
        simulator = OrbitalSimulator([sun, planet], dt=3600.0)
        
        # Run short simulation
        simulator.run_simulation(5 * 24 * 3600)  # 5 days
        
        # Visualize with close-up view
        fig, ax = simulator.visualize(use_3d=True, realistic_space=True, interactive=True)
        ax.set_title(f'🔍 {planet_name} Close-up View', color='white', fontsize=16)
        plt.show()

def planet_comparison():
    """Compare all planets side by side"""
    print("\n📊 Planet Comparison")
    print("=" * 25)
    
    # Create a system with all planets
    simulator = OrbitalSimulator([], dt=3600.0)
    simulator.create_realistic_space_scene()
    
    # Run simulation
    simulator.run_simulation(10 * 24 * 3600)  # 10 days
    
    # Create comparison visualization
    fig, ax = simulator.visualize(use_3d=True, realistic_space=True, interactive=True)
    ax.set_title('🌌 Complete Solar System - All Planets', color='white', fontsize=16)
    plt.show()

def realistic_animation():
    """Create realistic animation of the complete solar system"""
    print("\n🎬 Realistic Solar System Animation")
    print("=" * 40)
    
    # Create simulator
    simulator = OrbitalSimulator([], dt=1800.0)  # 30 min time step for smoother animation
    simulator.create_realistic_space_scene()
    
    print("Creating realistic animation with all planets...")
    print("Features:")
    print("  - All 8 planets + Moon")
    print("  - Realistic surface appearances")
    print("  - Smooth orbital motion")
    print("  - Interactive 3D controls")
    
    # Create 20-second animation
    anim = simulator.animate_simulation(duration=20, fps=24, save_gif=False)
    
    return anim

def zoom_to_planets():
    """Demonstrate zooming to different planets"""
    print("\n🔍 Zoom to Planets Demo")
    print("=" * 30)
    
    # Create complete solar system
    simulator = OrbitalSimulator([], dt=3600.0)
    simulator.create_realistic_space_scene()
    simulator.run_simulation(15 * 24 * 3600)  
    
    
    fig, ax = simulator.visualize(use_3d=True, realistic_space=True, interactive=True)
    ax.set_title('🌌 Interactive Solar System - Zoom to Explore!', color='white', fontsize=16)
    plt.show()

if __name__ == "__main__":
    print("🌌 Realistic Solar System Demo")
    print("=" * 35)
