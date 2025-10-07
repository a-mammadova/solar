"""
Orbital Mechanics Simulator
A Python implementation of orbital mechanics with gravitational forces
Supports both 2D and 3D simulations
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from scipy.integrate import solve_ivp
from dataclasses import dataclass
from typing import List, Tuple, Union
import math
import time

# Physical constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
AU = 1.496e11    # Astronomical unit (m)
EARTH_MASS = 5.972e24  # Earth mass (kg)
SUN_MASS = 1.989e30    # Sun mass (kg)

@dataclass
class CelestialBody:
    """Represents a celestial body with mass, position, and velocity"""
    name: str
    mass: float  # kg
    position: np.ndarray  # [x, y, z] in meters (3D) or [x, y] (2D)
    velocity: np.ndarray  # [vx, vy, vz] in m/s (3D) or [vx, vy] (2D)
    radius: float = 0.0  # visual radius for plotting
    color: str = 'blue'
    is_3d: bool = True  # Whether this body exists in 3D space
    
    def __post_init__(self):
        """Ensure position and velocity are numpy arrays with correct dimensions"""
        self.position = np.array(self.position, dtype=float)
        self.velocity = np.array(self.velocity, dtype=float)
        
        # Ensure 3D coordinates
        if len(self.position) == 2:
            self.position = np.append(self.position, 0.0)
            self.is_3d = False
        elif len(self.position) == 3:
            self.is_3d = True
        else:
            raise ValueError("Position must be 2D [x,y] or 3D [x,y,z]")
            
        if len(self.velocity) == 2:
            self.velocity = np.append(self.velocity, 0.0)
        elif len(self.velocity) == 3:
            pass  # Already 3D
        else:
            raise ValueError("Velocity must be 2D [vx,vy] or 3D [vx,vy,vz]")

class PhysicsEngine:
    """Handles the physics calculations for orbital mechanics"""
    
    def __init__(self, bodies: List[CelestialBody]):
        self.bodies = bodies
        self.time = 0.0
        
    def gravitational_force(self, body1: CelestialBody, body2: CelestialBody) -> np.ndarray:
        """
        Calculate gravitational force between two bodies
        Returns force vector on body1 due to body2
        """
        # Vector from body1 to body2
        r_vec = body2.position - body1.position
        r = np.linalg.norm(r_vec)
        
        # Avoid division by zero for overlapping bodies
        if r < 1e6:  # 1000 km minimum distance
            return np.zeros(3)
        
        # Gravitational force magnitude
        force_magnitude = G * body1.mass * body2.mass / (r**2)
        
        # Force direction (unit vector from body1 to body2)
        force_direction = r_vec / r
        
        return force_magnitude * force_direction
    
    def calculate_forces(self, body: CelestialBody) -> np.ndarray:
        """
        Calculate net gravitational force on a body from all other bodies
        """
        net_force = np.zeros(3)
        
        for other_body in self.bodies:
            if other_body != body:
                force = self.gravitational_force(body, other_body)
                net_force += force
                
        return net_force
    
    def acceleration(self, body: CelestialBody) -> np.ndarray:
        """
        Calculate acceleration of a body due to gravitational forces
        F = ma, so a = F/m
        """
        force = self.calculate_forces(body)
        return force / body.mass
    
    def update_positions_velocities(self, dt: float):
        """
        Update positions and velocities using Verlet integration
        More stable than Euler's method for orbital mechanics
        """
        # Store current positions and velocities
        old_positions = [body.position.copy() for body in self.bodies]
        old_velocities = [body.velocity.copy() for body in self.bodies]
        
        # Calculate accelerations
        accelerations = [self.acceleration(body) for body in self.bodies]
        
        # Update velocities using current acceleration
        for i, body in enumerate(self.bodies):
            body.velocity += accelerations[i] * dt
        
        # Update positions using new velocities
        for i, body in enumerate(self.bodies):
            body.position += body.velocity * dt
        
        # Calculate new accelerations with updated positions
        new_accelerations = [self.acceleration(body) for body in self.bodies]
        
        # Correct velocities using average acceleration
        for i, body in enumerate(self.bodies):
            avg_acceleration = (accelerations[i] + new_accelerations[i]) / 2
            body.velocity = old_velocities[i] + avg_acceleration * dt
        
        self.time += dt
    
    def get_orbital_energy(self, body: CelestialBody) -> float:
        """
        Calculate total orbital energy (kinetic + potential) of a body
        """
        # Kinetic energy
        kinetic = 0.5 * body.mass * np.dot(body.velocity, body.velocity)
        
        # Potential energy
        potential = 0.0
        for other_body in self.bodies:
            if other_body != body:
                r = np.linalg.norm(body.position - other_body.position)
                if r > 1e6:  # Avoid division by zero
                    potential -= G * body.mass * other_body.mass / r
        
        return kinetic + potential
    
    def get_angular_momentum(self, body: CelestialBody) -> np.ndarray:
        """
        Calculate angular momentum vector of a body
        """
        return body.mass * np.cross(body.position, body.velocity)

class OrbitalSimulator:
    """Main simulator class that handles the simulation loop and visualization"""
    
    def __init__(self, bodies: List[CelestialBody], dt: float = 3600.0):
        """
        Initialize the simulator
        
        Args:
            bodies: List of celestial bodies
            dt: Time step in seconds (default: 1 hour)
        """
        self.physics_engine = PhysicsEngine(bodies)
        self.dt = dt
        self.time = 0.0
        self.trajectories = {body.name: [] for body in bodies}
        
    def step(self):
        """Advance the simulation by one time step"""
        # Store current positions for trajectory tracking
        for body in self.physics_engine.bodies:
            self.trajectories[body.name].append(body.position.copy())
        
        # Update physics
        self.physics_engine.update_positions_velocities(self.dt)
        self.time += self.dt
    
    def run_simulation(self, duration: float, steps_per_frame: int = 1):
        """
        Run the simulation for a specified duration
        
        Args:
            duration: Simulation duration in seconds
            steps_per_frame: Number of physics steps per visualization frame
        """
        total_steps = int(duration / self.dt)
        
        for step in range(total_steps):
            self.step()
            
            # Print progress every 10% of simulation
            if step % (total_steps // 10) == 0:
                progress = (step / total_steps) * 100
                print(f"Simulation progress: {progress:.1f}%")
    
    def create_solar_system(self):
        """Create a simple solar system with Sun, Earth, and Moon"""
        # Clear existing bodies
        self.physics_engine.bodies.clear()
        self.trajectories.clear()
        
        # Sun at center
        sun = CelestialBody(
            name="Sun",
            mass=SUN_MASS,
            position=[0, 0],
            velocity=[0, 0],
            radius=20,
            color='yellow'
        )
        
        # Earth in circular orbit
        earth_distance = 1.496e11  # 1 AU
        earth_speed = np.sqrt(G * SUN_MASS / earth_distance)
        earth = CelestialBody(
            name="Earth",
            mass=EARTH_MASS,
            position=[earth_distance, 0],
            velocity=[0, earth_speed],
            radius=5,
            color='blue'
        )
        
        # Moon orbiting Earth
        moon_distance = 3.844e8  # 384,400 km
        moon_speed = np.sqrt(G * EARTH_MASS / moon_distance) + earth_speed
        moon = CelestialBody(
            name="Moon",
            mass=7.342e22,  # Moon mass
            position=[earth_distance + moon_distance, 0],
            velocity=[0, moon_speed],
            radius=2,
            color='gray'
        )
        
        # Add bodies to simulation
        self.physics_engine.bodies = [sun, earth, moon]
        self.trajectories = {body.name: [] for body in self.physics_engine.bodies}
    
    def create_3d_solar_system(self):
        """Create a 3D solar system with inclined orbits"""
        # Clear existing bodies
        self.physics_engine.bodies.clear()
        self.trajectories.clear()
        
        # Sun at center
        sun = CelestialBody(
            name="Sun",
            mass=SUN_MASS,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            radius=20,
            color='yellow',
            is_3d=True
        )
        
        # Earth in inclined orbit
        earth_distance = 1.496e11  # 1 AU
        earth_speed = np.sqrt(G * SUN_MASS / earth_distance)
        # Add some inclination and 3D motion
        earth = CelestialBody(
            name="Earth",
            mass=EARTH_MASS,
            position=[earth_distance, 0, 0],
            velocity=[0, earth_speed, 0],
            radius=5,
            color='blue',
            is_3d=True
        )
        
        # Moon with 3D orbital motion
        moon_distance = 3.844e8  # 384,400 km
        moon_speed = np.sqrt(G * EARTH_MASS / moon_distance) + earth_speed
        # Moon with some Z-component for 3D effect
        moon = CelestialBody(
            name="Moon",
            mass=7.342e22,
            position=[earth_distance + moon_distance, 0, 0],
            velocity=[0, moon_speed, 1000],  # Small Z velocity for 3D motion
            radius=2,
            color='gray',
            is_3d=True
        )
        
        # Add a planet with inclined orbit
        planet_distance = 2.5 * AU
        planet_speed = np.sqrt(G * SUN_MASS / planet_distance) * 0.8  # Slower for elliptical orbit
        planet = CelestialBody(
            name="Mars",
            mass=EARTH_MASS * 0.1,
            position=[planet_distance, 0, planet_distance * 0.1],  # Inclined position
            velocity=[0, planet_speed, planet_speed * 0.1],  # Inclined velocity
            radius=4,
            color='red',
            is_3d=True
        )
        
        # Add bodies to simulation
        self.physics_engine.bodies = [sun, earth, moon, planet]
        self.trajectories = {body.name: [] for body in self.physics_engine.bodies}
    
    def visualize(self, show_trajectories: bool = True, max_trajectory_points: int = 1000, 
                  use_3d: bool = None, realistic_space: bool = True, interactive: bool = True):
        """
        Create a visualization of the current state with realistic space appearance
        
        Args:
            show_trajectories: Whether to show orbital trajectories
            max_trajectory_points: Maximum number of trajectory points to display
            use_3d: Whether to use 3D visualization (auto-detect if None)
            realistic_space: Whether to use realistic space colors and styling
            interactive: Whether to enable interactive zoom/pan controls
        """
        # Auto-detect 3D if not specified
        if use_3d is None:
            use_3d = any(body.is_3d for body in self.physics_engine.bodies)
        
        if use_3d:
            fig = plt.figure(figsize=(14, 12), facecolor='black')
            ax = fig.add_subplot(111, projection='3d')
        else:
            fig, ax = plt.subplots(figsize=(14, 12), facecolor='black')
        
        # Set dark space background
        if realistic_space:
            ax.set_facecolor('black')
            fig.patch.set_facecolor('black')
            
            # Add starfield background effect
            self._add_starfield(ax, use_3d)
        
        # Plot trajectories with realistic colors
        if show_trajectories:
            for body_name, trajectory in self.trajectories.items():
                if len(trajectory) > 1:
                    # Limit trajectory points for performance
                    trajectory_points = trajectory[-max_trajectory_points:]
                    trajectory_array = np.array(trajectory_points)
                    
                    # Convert to AU for better visualization
                    trajectory_au = trajectory_array / AU
                    
                    # Get trajectory color based on body
                    traj_color = self._get_trajectory_color(body_name)
                    
                    if use_3d:
                        ax.plot(trajectory_au[:, 0], trajectory_au[:, 1], trajectory_au[:, 2],
                               alpha=0.4, linewidth=0.8, color=traj_color)
                    else:
                        ax.plot(trajectory_au[:, 0], trajectory_au[:, 1], 
                               alpha=0.4, linewidth=0.8, color=traj_color)
        
        # Plot celestial bodies with realistic appearance
        for body in self.physics_engine.bodies:
            pos_au = body.position / AU
            body_color, body_size = self._get_realistic_body_properties(body)
            
            if use_3d:
                # Create realistic 3D sphere effect
                self._plot_realistic_body_3d(ax, pos_au, body_color, body_size, body.name)
            else:
                # Create realistic 2D body with glow effect
                self._plot_realistic_body_2d(ax, pos_au, body_color, body_size, body.name)
        
        # Set realistic space styling
        if realistic_space:
            self._style_space_plot(ax, use_3d)
        
        # Set axis labels and title
        if use_3d:
            ax.set_xlabel('X Position (AU)', color='white', fontsize=10)
            ax.set_ylabel('Y Position (AU)', color='white', fontsize=10)
            ax.set_zlabel('Z Position (AU)', color='white', fontsize=10)
            ax.set_title(f'🌌 Realistic Space Simulation (t = {self.time/86400:.1f} days)', 
                        color='white', fontsize=14, pad=20)
        else:
            ax.set_xlabel('X Position (AU)', color='white', fontsize=10)
            ax.set_ylabel('Y Position (AU)', color='white', fontsize=10)
            ax.set_title(f'🌌 Realistic Space Simulation (t = {self.time/86400:.1f} days)', 
                        color='white', fontsize=14, pad=20)
        
        # Set reasonable axis limits
        all_positions = [body.position / AU for body in self.physics_engine.bodies]
        if all_positions:
            positions_array = np.array(all_positions)
            max_coord = np.max(np.abs(positions_array)) * 1.2
            if use_3d:
                ax.set_xlim(-max_coord, max_coord)
                ax.set_ylim(-max_coord, max_coord)
                ax.set_zlim(-max_coord, max_coord)
            else:
                ax.set_xlim(-max_coord, max_coord)
                ax.set_ylim(-max_coord, max_coord)
        
        if not use_3d:
            ax.set_aspect('equal')
        
        # Enable interactive controls
        if interactive:
            self._enable_interactive_controls(fig, ax, use_3d)
            
            # Add touchpad-friendly instructions
            fig.text(0.5, 0.95, '🔍 Interactive Controls: Scroll to zoom, Drag to pan, Mouse drag to rotate (3D)', 
                    ha='center', fontsize=10, color='white', alpha=0.8,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        plt.tight_layout()
        return fig, ax
    
    def _enable_interactive_controls(self, fig, ax, use_3d):
        """Enable interactive zoom and pan controls"""
        # For 3D plots, enable rotation and zoom
        if use_3d:
            # Enable 3D rotation and zoom
            ax.mouse_init()
            
            # Add custom zoom controls
            self._add_zoom_controls(fig, ax)
        else:
            # Enable 2D zoom and pan
            ax.set_navigate(True)
            
            # Add custom zoom controls
            self._add_zoom_controls(fig, ax)
    
    def _add_zoom_controls(self, fig, ax):
        """Add custom zoom controls for better touchpad support"""
        # Create zoom control buttons
        from matplotlib.widgets import Button
        
        # Zoom in button
        ax_zoom_in = plt.axes([0.02, 0.02, 0.1, 0.04])
        btn_zoom_in = Button(ax_zoom_in, 'Zoom In', color='lightblue')
        btn_zoom_in.on_clicked(lambda x: self._zoom_in(ax))
        
        # Zoom out button  
        ax_zoom_out = plt.axes([0.13, 0.02, 0.1, 0.04])
        btn_zoom_out = Button(ax_zoom_out, 'Zoom Out', color='lightblue')
        btn_zoom_out.on_clicked(lambda x: self._zoom_out(ax))
        
        # Reset view button
        ax_reset = plt.axes([0.24, 0.02, 0.1, 0.04])
        btn_reset = Button(ax_reset, 'Reset View', color='lightgreen')
        btn_reset.on_clicked(lambda x: self._reset_view(ax))
        
        # Add instructions
        fig.text(0.35, 0.03, 'Touchpad: Scroll to zoom, Drag to pan', 
                fontsize=8, color='white', alpha=0.7)
    
    def _zoom_in(self, ax):
        """Zoom in on the current view"""
        if hasattr(ax, 'get_xlim'):  # 2D plot
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 0.8
            y_range = (ylim[1] - ylim[0]) * 0.8
            
            ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
        else:  # 3D plot
            # For 3D, we can't easily zoom programmatically
            # The user will need to use mouse controls
            pass
        
        ax.figure.canvas.draw()
    
    def _zoom_out(self, ax):
        """Zoom out from the current view"""
        if hasattr(ax, 'get_xlim'):  # 2D plot
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 1.25
            y_range = (ylim[1] - ylim[0]) * 1.25
            
            ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
        else:  # 3D plot
            # For 3D, we can't easily zoom programmatically
            # The user will need to use mouse controls
            pass
        
        ax.figure.canvas.draw()
    
    def _reset_view(self, ax):
        """Reset the view to show all bodies"""
        # Get all body positions
        all_positions = [body.position / AU for body in self.physics_engine.bodies]
        if all_positions:
            positions_array = np.array(all_positions)
            max_coord = np.max(np.abs(positions_array)) * 1.2
            
            if hasattr(ax, 'set_xlim'):  # 2D plot
                ax.set_xlim(-max_coord, max_coord)
                ax.set_ylim(-max_coord, max_coord)
            else:  # 3D plot
                ax.set_xlim(-max_coord, max_coord)
                ax.set_ylim(-max_coord, max_coord)
                ax.set_zlim(-max_coord, max_coord)
        
        ax.figure.canvas.draw()
    
    def animate_simulation(self, duration: float, fps: int = 30, save_gif: bool = False, 
                          filename: str = "orbital_animation.gif"):
        """
        Create a realistic 3D animation of the orbital mechanics simulation
        
        Args:
            duration: Animation duration in seconds
            fps: Frames per second for animation
            save_gif: Whether to save animation as GIF
            filename: Output filename for saved animation
        """
        print(f"🎬 Creating realistic 3D animation ({duration}s, {fps} FPS)...")
        
        # Calculate animation parameters
        total_frames = int(duration * fps)
        frame_interval = 1000 / fps  # milliseconds per frame
        simulation_dt = self.dt / fps  # Smaller time step for smooth animation
        
        # Create figure and 3D axis
        fig = plt.figure(figsize=(16, 12), facecolor='black')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('black')
        
        # Add starfield
        self._add_starfield(ax, True)
        
        # Initialize animation data
        animation_data = {
            'positions': {body.name: [] for body in self.physics_engine.bodies},
            'current_frame': 0,
            'bodies': self.physics_engine.bodies.copy(),
            'trajectories': {body.name: [] for body in self.physics_engine.bodies}
        }
        
        # Store initial positions
        for body in self.physics_engine.bodies:
            animation_data['positions'][body.name].append(body.position.copy())
            animation_data['trajectories'][body.name].append(body.position.copy())
        
        def animate(frame):
            """Animation function called for each frame"""
            ax.clear()
            ax.set_facecolor('black')
            
            # Add starfield for each frame
            self._add_starfield(ax, True)
            
            # Update simulation for this frame
            for _ in range(fps):
                self.step()
            
            # Store current positions
            for body in self.physics_engine.bodies:
                animation_data['positions'][body.name].append(body.position.copy())
                animation_data['trajectories'][body.name].append(body.position.copy())
            
            # Plot trajectories (last 1000 points for performance)
            for body_name, trajectory in animation_data['trajectories'].items():
                if len(trajectory) > 1:
                    recent_trajectory = trajectory[-1000:]  # Limit for performance
                    trajectory_array = np.array(recent_trajectory)
                    trajectory_au = trajectory_array / AU
                    
                    traj_color = self._get_trajectory_color(body_name)
                    ax.plot(trajectory_au[:, 0], trajectory_au[:, 1], trajectory_au[:, 2],
                           alpha=0.6, linewidth=1, color=traj_color)
            
            # Plot current positions with realistic effects
            for body in self.physics_engine.bodies:
                pos_au = body.position / AU
                body_color, body_size = self._get_realistic_body_properties(body)
                
                # Create realistic 3D body with glow
                self._plot_realistic_body_3d(ax, pos_au, body_color, body_size, body.name)
            
            # Set realistic space styling
            self._style_space_plot(ax, True)
            
            # Set axis properties
            ax.set_xlabel('X Position (AU)', color='white', fontsize=10)
            ax.set_ylabel('Y Position (AU)', color='white', fontsize=10)
            ax.set_zlabel('Z Position (AU)', color='white', fontsize=10)
            
            # Dynamic title with time
            current_time = self.time / 86400  # Convert to days
            ax.set_title(f'🌌 Realistic 3D Orbital Animation (t = {current_time:.1f} days)', 
                        color='white', fontsize=14, pad=20)
            
            # Set reasonable axis limits
            all_positions = [body.position / AU for body in self.physics_engine.bodies]
            if all_positions:
                positions_array = np.array(all_positions)
                max_coord = np.max(np.abs(positions_array)) * 1.2
                ax.set_xlim(-max_coord, max_coord)
                ax.set_ylim(-max_coord, max_coord)
                ax.set_zlim(-max_coord, max_coord)
            
            animation_data['current_frame'] = frame
            
            return ax,
        
        # Create animation
        print("Rendering animation frames...")
        anim = animation.FuncAnimation(fig, animate, frames=total_frames, 
                                    interval=frame_interval, blit=False, repeat=True)
        
        # Save animation if requested
        if save_gif:
            print(f"Saving animation as {filename}...")
            anim.save(filename, writer='pillow', fps=fps)
            print(f"Animation saved as {filename}")
        
        # Show animation
        plt.show()
        
        return anim
    
    def create_realistic_space_scene(self):
        """Create a more realistic space scene with enhanced effects"""
        # Create 3D solar system with realistic parameters
        self.physics_engine.bodies.clear()
        self.trajectories.clear()
        
        # Sun with realistic properties
        sun = CelestialBody(
            name="Sun",
            mass=SUN_MASS,
            position=[0, 0, 0],
            velocity=[0, 0, 0],
            radius=30,  # Larger for visibility
            color='#FFD700',
            is_3d=True
        )
        
        # Mercury
        mercury_distance = 0.39 * AU
        mercury_speed = np.sqrt(G * SUN_MASS / mercury_distance)
        mercury = CelestialBody(
            name="Mercury",
            mass=EARTH_MASS * 0.055,
            position=[mercury_distance, 0, 0],
            velocity=[0, mercury_speed, 0],
            radius=4,
            color='#8C7853',
            is_3d=True
        )
        
        # Venus
        venus_distance = 0.72 * AU
        venus_speed = np.sqrt(G * SUN_MASS / venus_distance)
        venus = CelestialBody(
            name="Venus",
            mass=EARTH_MASS * 0.815,
            position=[venus_distance, 0, 0],
            velocity=[0, venus_speed, 0],
            radius=7,
            color='#FF8C00',
            is_3d=True
        )
        
        # Earth with realistic orbit
        earth_distance = 1.0 * AU
        earth_speed = np.sqrt(G * SUN_MASS / earth_distance)
        earth = CelestialBody(
            name="Earth",
            mass=EARTH_MASS,
            position=[earth_distance, 0, 0],
            velocity=[0, earth_speed, 0],
            radius=8,
            color='#4169E1',
            is_3d=True
        )
        
        # Moon with 3D orbital motion
        moon_distance = 3.844e8
        moon_speed = np.sqrt(G * EARTH_MASS / moon_distance) + earth_speed
        moon = CelestialBody(
            name="Moon",
            mass=7.342e22,
            position=[earth_distance + moon_distance, 0, 0],
            velocity=[0, moon_speed, 2000],  # 3D motion
            radius=3,
            color='#C0C0C0',
            is_3d=True
        )
        
        # Mars with inclined orbit
        mars_distance = 1.52 * AU
        mars_speed = np.sqrt(G * SUN_MASS / mars_distance)
        mars = CelestialBody(
            name="Mars",
            mass=EARTH_MASS * 0.107,
            position=[mars_distance, 0, mars_distance * 0.05],
            velocity=[0, mars_speed, mars_speed * 0.05],
            radius=6,
            color='#CD5C5C',
            is_3d=True
        )
        
        # Jupiter
        jupiter_distance = 5.2 * AU
        jupiter_speed = np.sqrt(G * SUN_MASS / jupiter_distance)
        jupiter = CelestialBody(
            name="Jupiter",
            mass=EARTH_MASS * 317.8,
            position=[jupiter_distance, 0, 0],
            velocity=[0, jupiter_speed, 0],
            radius=20,
            color='#D2691E',
            is_3d=True
        )
        
        # Saturn
        saturn_distance = 9.58 * AU
        saturn_speed = np.sqrt(G * SUN_MASS / saturn_distance)
        saturn = CelestialBody(
            name="Saturn",
            mass=EARTH_MASS * 95.2,
            position=[saturn_distance, 0, 0],
            velocity=[0, saturn_speed, 0],
            radius=18,
            color='#F4A460',
            is_3d=True
        )
        
        # Uranus
        uranus_distance = 19.2 * AU
        uranus_speed = np.sqrt(G * SUN_MASS / uranus_distance)
        uranus = CelestialBody(
            name="Uranus",
            mass=EARTH_MASS * 14.5,
            position=[uranus_distance, 0, 0],
            velocity=[0, uranus_speed, 0],
            radius=12,
            color='#4FD0E7',
            is_3d=True
        )
        
        # Neptune
        neptune_distance = 30.1 * AU
        neptune_speed = np.sqrt(G * SUN_MASS / neptune_distance)
        neptune = CelestialBody(
            name="Neptune",
            mass=EARTH_MASS * 17.1,
            position=[neptune_distance, 0, 0],
            velocity=[0, neptune_speed, 0],
            radius=12,
            color='#4169E1',
            is_3d=True
        )
        
        # Add all bodies to simulation
        self.physics_engine.bodies = [sun, mercury, venus, earth, moon, mars, 
                                     jupiter, saturn, uranus, neptune]
        self.trajectories = {body.name: [] for body in self.physics_engine.bodies}
    
    def _add_starfield(self, ax, use_3d):
        """Add a starfield background effect"""
        # Generate random star positions
        n_stars = 200
        if use_3d:
            stars_x = np.random.uniform(-10, 10, n_stars)
            stars_y = np.random.uniform(-10, 10, n_stars)
            stars_z = np.random.uniform(-10, 10, n_stars)
            ax.scatter(stars_x, stars_y, stars_z, c='white', s=0.1, alpha=0.6)
        else:
            stars_x = np.random.uniform(-10, 10, n_stars)
            stars_y = np.random.uniform(-10, 10, n_stars)
            ax.scatter(stars_x, stars_y, c='white', s=0.1, alpha=0.6)
    
    def _get_trajectory_color(self, body_name):
        """Get realistic trajectory color for each body"""
        colors = {
            'Sun': '#FFD700',      # Golden
            'Mercury': '#8C7853',  # Brown
            'Venus': '#FF8C00',    # Orange
            'Earth': '#4169E1',    # Royal blue
            'Moon': '#C0C0C0',     # Silver
            'Mars': '#CD5C5C',     # Indian red
            'Jupiter': '#D2691E',  # Saddle brown
            'Saturn': '#F4A460',   # Sandy brown
            'Uranus': '#4FD0E7',   # Light blue
            'Neptune': '#4169E1',  # Royal blue
            'Star 1': '#FFD700',   # Golden
            'Star 2': '#FFA500',   # Orange
            'Planet': '#87CEEB'    # Sky blue
        }
        return colors.get(body_name, '#FFFFFF')
    
    def _get_realistic_body_properties(self, body):
        """Get realistic color and size for celestial bodies"""
        # Realistic colors and sizes
        body_properties = {
            'Sun': ('#FFD700', 30),      # Golden yellow, large
            'Mercury': ('#8C7853', 4),   # Brown, small
            'Venus': ('#FF8C00', 7),     # Orange, medium-small
            'Earth': ('#4169E1', 8),     # Blue, medium
            'Moon': ('#C0C0C0', 3),      # Silver gray, small
            'Mars': ('#CD5C5C', 6),      # Red, medium-small
            'Jupiter': ('#D2691E', 20),  # Brown, large
            'Saturn': ('#F4A460', 18),   # Sandy brown, large
            'Uranus': ('#4FD0E7', 12),   # Light blue, medium-large
            'Neptune': ('#4169E1', 12),  # Royal blue, medium-large
            'Star 1': ('#FFD700', 20),   # Golden, large
            'Star 2': ('#FFA500', 18),   # Orange, large
            'Planet': ('#87CEEB', 5)     # Sky blue, small
        }
        
        color, base_size = body_properties.get(body.name, ('#FFFFFF', 5))
        
        # Scale size based on actual radius
        size = max(base_size, body.radius * 2)
        
        return color, size
    
    def _plot_realistic_body_3d(self, ax, pos, color, size, name):
        """Plot realistic 3D celestial body with realistic surface appearance"""
        # Create realistic planet surface
        if name in ['Sun']:
            # Sun with corona effect
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*2.5)**2, c='#FFD700', alpha=0.1)  # Outer corona
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*2)**2, c='#FFA500', alpha=0.2)     # Middle corona
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*1.5)**2, c='#FFD700', alpha=0.4)  # Inner corona
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#FFFF00', alpha=0.9, edgecolors='#FF4500', linewidth=1)
        
        elif name in ['Earth']:
            # Earth with continents and atmosphere
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*1.3)**2, c='#87CEEB', alpha=0.3)  # Atmosphere
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#4169E1', alpha=0.9, edgecolors='#228B22', linewidth=0.5)
            # Add some green continents
            ax.scatter(pos[0] + size*0.1, pos[1] + size*0.1, pos[2], 
                      s=(size*0.3)**2, c='#228B22', alpha=0.8)
            ax.scatter(pos[0] - size*0.1, pos[1] - size*0.1, pos[2], 
                      s=(size*0.2)**2, c='#32CD32', alpha=0.7)
        
        elif name in ['Mars']:
            # Mars with realistic red surface and polar caps
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#CD5C5C', alpha=0.9, edgecolors='#8B0000', linewidth=0.5)
            # Polar ice caps
            ax.scatter(pos[0], pos[1] + size*0.3, pos[2], 
                      s=(size*0.4)**2, c='#F0F8FF', alpha=0.8)
            ax.scatter(pos[0], pos[1] - size*0.3, pos[2], 
                      s=(size*0.4)**2, c='#F0F8FF', alpha=0.8)
            # Surface features
            ax.scatter(pos[0] + size*0.2, pos[1], pos[2], 
                      s=(size*0.1)**2, c='#8B0000', alpha=0.6)
        
        elif name in ['Moon']:
            # Moon with realistic gray surface and craters
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#C0C0C0', alpha=0.9, edgecolors='#A9A9A9', linewidth=0.5)
            # Craters
            ax.scatter(pos[0] + size*0.2, pos[1] + size*0.1, pos[2], 
                      s=(size*0.2)**2, c='#A9A9A9', alpha=0.7)
            ax.scatter(pos[0] - size*0.15, pos[1] - size*0.2, pos[2], 
                      s=(size*0.15)**2, c='#A9A9A9', alpha=0.6)
        
        elif name in ['Mercury']:
            # Mercury with rocky surface
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#8C7853', alpha=0.9, edgecolors='#696969', linewidth=0.5)
            # Surface features
            ax.scatter(pos[0] + size*0.1, pos[1], pos[2], 
                      s=(size*0.1)**2, c='#696969', alpha=0.7)
        
        elif name in ['Venus']:
            # Venus with thick atmosphere
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*1.2)**2, c='#FFA500', alpha=0.3)  # Atmosphere
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#FF8C00', alpha=0.9, edgecolors='#FF4500', linewidth=0.5)
        
        elif name in ['Jupiter']:
            # Jupiter with bands and Great Red Spot
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#D2691E', alpha=0.9, edgecolors='#8B4513', linewidth=0.5)
            # Atmospheric bands
            ax.scatter(pos[0], pos[1] + size*0.2, pos[2], 
                      s=(size*0.8)**2, c='#CD853F', alpha=0.7)
            ax.scatter(pos[0], pos[1] - size*0.2, pos[2], 
                      s=(size*0.8)**2, c='#A0522D', alpha=0.7)
            # Great Red Spot
            ax.scatter(pos[0] + size*0.3, pos[1], pos[2], 
                      s=(size*0.3)**2, c='#DC143C', alpha=0.8)
        
        elif name in ['Saturn']:
            # Saturn with rings
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#F4A460', alpha=0.9, edgecolors='#D2691E', linewidth=0.5)
            # Rings
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*1.8)**2, c='#DEB887', alpha=0.3)
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*2.2)**2, c='#F5DEB3', alpha=0.2)
        
        elif name in ['Uranus']:
            # Uranus with blue-green color
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#4FD0E7', alpha=0.9, edgecolors='#20B2AA', linewidth=0.5)
        
        elif name in ['Neptune']:
            # Neptune with deep blue color
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#4169E1', alpha=0.9, edgecolors='#0000CD', linewidth=0.5)
        
        elif name in ['Mercury']:
            # Mercury with rocky surface
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#8C7853', alpha=0.9, edgecolors='#696969', linewidth=0.5)
            # Surface features
            ax.scatter(pos[0] + size*0.1, pos[1], pos[2], 
                      s=(size*0.1)**2, c='#696969', alpha=0.7)
        
        elif name in ['Venus']:
            # Venus with thick atmosphere
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*1.2)**2, c='#FFA500', alpha=0.3)  # Atmosphere
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#FF8C00', alpha=0.9, edgecolors='#FF4500', linewidth=0.5)
        
        elif name in ['Jupiter']:
            # Jupiter with bands and Great Red Spot
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#D2691E', alpha=0.9, edgecolors='#8B4513', linewidth=0.5)
            # Atmospheric bands
            ax.scatter(pos[0], pos[1] + size*0.2, pos[2], 
                      s=(size*0.8)**2, c='#CD853F', alpha=0.7)
            ax.scatter(pos[0], pos[1] - size*0.2, pos[2], 
                      s=(size*0.8)**2, c='#A0522D', alpha=0.7)
            # Great Red Spot
            ax.scatter(pos[0] + size*0.3, pos[1], pos[2], 
                      s=(size*0.3)**2, c='#DC143C', alpha=0.8)
        
        elif name in ['Saturn']:
            # Saturn with rings
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#F4A460', alpha=0.9, edgecolors='#D2691E', linewidth=0.5)
            # Rings
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*1.8)**2, c='#DEB887', alpha=0.3)
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=(size*2.2)**2, c='#F5DEB3', alpha=0.2)
        
        elif name in ['Uranus']:
            # Uranus with blue-green color
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#4FD0E7', alpha=0.9, edgecolors='#20B2AA', linewidth=0.5)
        
        elif name in ['Neptune']:
            # Neptune with deep blue color
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c='#4169E1', alpha=0.9, edgecolors='#0000CD', linewidth=0.5)
        
        else:
            # Default appearance for other bodies
            ax.scatter(pos[0], pos[1], pos[2], 
                      s=size**2, c=color, alpha=0.9, edgecolors='white', linewidth=0.5)
    
    def _plot_realistic_body_2d(self, ax, pos, color, size, name):
        """Plot realistic 2D celestial body with glow effect"""
        # Main body
        ax.scatter(pos[0], pos[1], s=size**2, c=color, alpha=0.9, 
                  edgecolors='white', linewidth=0.5)
        
        # Add glow effect for larger bodies
        if size > 10:  # Sun and large stars
            ax.scatter(pos[0], pos[1], s=(size*1.5)**2, c=color, alpha=0.3)
            ax.scatter(pos[0], pos[1], s=(size*2)**2, c=color, alpha=0.1)
    
    def _style_space_plot(self, ax, use_3d):
        """Apply realistic space styling to the plot"""
        # Set dark theme
        ax.tick_params(colors='white', labelsize=9)
        
        if use_3d:
            # 3D specific styling
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            
            # Make the panes transparent
            ax.xaxis.pane.set_edgecolor('gray')
            ax.yaxis.pane.set_edgecolor('gray')
            ax.zaxis.pane.set_edgecolor('gray')
            
            # Set grid
            ax.grid(True, alpha=0.1, color='gray')
        else:
            # 2D specific styling
            ax.grid(True, alpha=0.1, color='gray')
            ax.set_facecolor('black')

def main():
    """Main function to run the orbital mechanics simulator"""
    print("Orbital Mechanics Simulator - 3D Edition")
    print("=" * 50)
    
    # Create simulator
    simulator = OrbitalSimulator([], dt=3600.0)  # 1 hour time step
    
    # Create 3D solar system
    simulator.create_3d_solar_system()
    
    print(f"Created 3D solar system with {len(simulator.physics_engine.bodies)} bodies")
    for body in simulator.physics_engine.bodies:
        print(f"  - {body.name}: mass = {body.mass:.2e} kg, 3D = {body.is_3d}")
    
    # Run simulation for 180 days (shorter for 3D demo)
    print("\nRunning 3D simulation for 180 days...")
    simulator.run_simulation(180 * 24 * 3600)  # 180 days in seconds
    
    # Create realistic 3D animation
    print("\nCreating realistic 3D orbital animation...")
    print("Features: Realistic space background, smooth motion, glowing bodies, trailing paths")
    anim = simulator.animate_simulation(duration=20, fps=24, save_gif=False)
    
    # Also show static visualization
    print("\nCreating interactive 3D space visualization...")
    print("Controls: Touchpad scroll to zoom, drag to pan, mouse drag to rotate 3D view")
    fig, ax = simulator.visualize(use_3d=True, realistic_space=True, interactive=True)
    plt.show()
    
    # Print orbital energies and angular momentum
    print("\nOrbital energies:")
    for body in simulator.physics_engine.bodies:
        energy = simulator.physics_engine.get_orbital_energy(body)
        print(f"  {body.name}: {energy:.2e} J")
    
    print("\nAngular momentum vectors:")
    for body in simulator.physics_engine.bodies:
        if body.name != "Sun":  # Skip sun for angular momentum
            L = simulator.physics_engine.get_angular_momentum(body)
            print(f"  {body.name}: L = [{L[0]:.2e}, {L[1]:.2e}, {L[2]:.2e}] kg⋅m²/s")

if __name__ == "__main__":
    main()
