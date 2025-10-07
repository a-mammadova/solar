"""
Interactive GUI for Orbital Mechanics Simulator
User-friendly interface for both professionals and general users
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from orbital_simulator import OrbitalSimulator, CelestialBody, SUN_MASS, EARTH_MASS, AU
import json
import threading
import time

class OrbitalMechanicsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌌 Orbital Mechanics Simulator - Interactive Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Simulation variables
        self.simulator = None
        self.is_running = False
        self.simulation_thread = None
        
        # Create GUI elements
        self.create_widgets()
        self.create_menu()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel - Visualization
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_control_panel(left_panel)
        self.create_visualization_panel(right_panel)
        
    def create_control_panel(self, parent):
        """Create the control panel with simulation controls"""
        # Title
        title_label = ttk.Label(parent, text="🌌 Orbital Controls", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Scenario selection
        scenario_frame = ttk.LabelFrame(parent, text="Solar System Scenarios", padding=10)
        scenario_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.scenario_var = tk.StringVar(value="Complete Solar System")
        scenarios = [
            "Complete Solar System",
            "Inner Planets Only",
            "Gas Giants Only", 
            "Earth-Moon System",
            "Binary Star System",
            "Custom System"
        ]
        
        for scenario in scenarios:
            ttk.Radiobutton(scenario_frame, text=scenario, variable=self.scenario_var, 
                           value=scenario, command=self.on_scenario_change).pack(anchor=tk.W)
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(parent, text="Simulation Controls", padding=10)
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Time step control
        ttk.Label(sim_frame, text="Time Step (hours):").pack(anchor=tk.W)
        self.dt_var = tk.DoubleVar(value=1.0)
        dt_scale = ttk.Scale(sim_frame, from_=0.1, to=24.0, variable=self.dt_var, 
                            orient=tk.HORIZONTAL)
        dt_scale.pack(fill=tk.X, pady=(0, 5))
        
        # Speed control
        ttk.Label(sim_frame, text="Simulation Speed:").pack(anchor=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(sim_frame, from_=0.1, to=10.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL)
        speed_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="▶ Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(button_frame, text="⏸ Pause", command=self.pause_simulation, 
                                      state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_button = ttk.Button(button_frame, text="🔄 Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT)
        
        # Visualization options
        vis_frame = ttk.LabelFrame(parent, text="Visualization Options", padding=10)
        vis_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.show_trajectories = tk.BooleanVar(value=True)
        ttk.Checkbutton(vis_frame, text="Show Trajectories", variable=self.show_trajectories).pack(anchor=tk.W)
        
        self.show_labels = tk.BooleanVar(value=True)
        ttk.Checkbutton(vis_frame, text="Show Planet Labels", variable=self.show_labels).pack(anchor=tk.W)
        
        self.realistic_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(vis_frame, text="Realistic Appearance", variable=self.realistic_mode).pack(anchor=tk.W)
        
        # Planet information
        info_frame = ttk.LabelFrame(parent, text="Planet Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, height=10, width=30, wrap=tk.WORD, 
                                bg='#2a2a2a', fg='white', font=('Arial', 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Add planet info
        self.update_planet_info()
        
    def create_visualization_panel(self, parent):
        """Create the visualization panel"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 8), facecolor='black')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('black')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Simulation", command=self.save_simulation)
        file_menu.add_command(label="Load Simulation", command=self.load_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Export Animation", command=self.export_animation)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Planet Builder", command=self.open_planet_builder)
        tools_menu.add_command(label="Orbit Calculator", command=self.open_orbit_calculator)
        tools_menu.add_command(label="Collision Simulator", command=self.open_collision_simulator)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
        
    def on_scenario_change(self):
        """Handle scenario selection change"""
        scenario = self.scenario_var.get()
        self.create_scenario(scenario)
        self.update_visualization()
        
    def create_scenario(self, scenario_name):
        """Create the selected scenario"""
        if scenario_name == "Complete Solar System":
            self.simulator = OrbitalSimulator([], dt=self.dt_var.get() * 3600)
            self.simulator.create_realistic_space_scene()
            
        elif scenario_name == "Inner Planets Only":
            self.simulator = OrbitalSimulator([], dt=self.dt_var.get() * 3600)
            self.create_inner_planets()
            
        elif scenario_name == "Gas Giants Only":
            self.simulator = OrbitalSimulator([], dt=self.dt_var.get() * 3600)
            self.create_gas_giants()
            
        elif scenario_name == "Earth-Moon System":
            self.simulator = OrbitalSimulator([], dt=self.dt_var.get() * 3600)
            self.create_earth_moon_system()
            
        elif scenario_name == "Binary Star System":
            self.simulator = OrbitalSimulator([], dt=self.dt_var.get() * 3600)
            self.create_binary_star_system()
            
        elif scenario_name == "Custom System":
            self.open_planet_builder()
            
    def create_inner_planets(self):
        """Create inner planets scenario"""
        sun = CelestialBody("Sun", SUN_MASS, [0, 0, 0], [0, 0, 0], 25, '#FFD700', is_3d=True)
        mercury = CelestialBody("Mercury", EARTH_MASS * 0.055, [0.39 * AU, 0, 0], 
                               [0, 47870, 0], 4, '#8C7853', is_3d=True)
        venus = CelestialBody("Venus", EARTH_MASS * 0.815, [0.72 * AU, 0, 0], 
                             [0, 35020, 0], 7, '#FF8C00', is_3d=True)
        earth = CelestialBody("Earth", EARTH_MASS, [1.0 * AU, 0, 0], 
                             [0, 29780, 0], 8, '#4169E1', is_3d=True)
        mars = CelestialBody("Mars", EARTH_MASS * 0.107, [1.52 * AU, 0, 0], 
                            [0, 24077, 0], 6, '#CD5C5C', is_3d=True)
        
        self.simulator.physics_engine.bodies = [sun, mercury, venus, earth, mars]
        self.simulator.trajectories = {body.name: [] for body in self.simulator.physics_engine.bodies}
        
    def create_gas_giants(self):
        """Create gas giants scenario"""
        sun = CelestialBody("Sun", SUN_MASS, [0, 0, 0], [0, 0, 0], 30, '#FFD700', is_3d=True)
        jupiter = CelestialBody("Jupiter", EARTH_MASS * 317.8, [5.2 * AU, 0, 0], 
                               [0, 13070, 0], 25, '#D2691E', is_3d=True)
        saturn = CelestialBody("Saturn", EARTH_MASS * 95.2, [9.58 * AU, 0, 0], 
                              [0, 9680, 0], 22, '#F4A460', is_3d=True)
        uranus = CelestialBody("Uranus", EARTH_MASS * 14.5, [19.2 * AU, 0, 0], 
                              [0, 6800, 0], 15, '#4FD0E7', is_3d=True)
        neptune = CelestialBody("Neptune", EARTH_MASS * 17.1, [30.1 * AU, 0, 0], 
                               [0, 5430, 0], 15, '#4169E1', is_3d=True)
        
        self.simulator.physics_engine.bodies = [sun, jupiter, saturn, uranus, neptune]
        self.simulator.trajectories = {body.name: [] for body in self.simulator.physics_engine.bodies}
        
    def create_earth_moon_system(self):
        """Create Earth-Moon system"""
        earth = CelestialBody("Earth", EARTH_MASS, [0, 0, 0], [0, 0, 0], 10, '#4169E1', is_3d=True)
        moon = CelestialBody("Moon", 7.342e22, [3.844e8, 0, 0], 
                            [0, 1022, 0], 3, '#C0C0C0', is_3d=True)
        
        self.simulator.physics_engine.bodies = [earth, moon]
        self.simulator.trajectories = {body.name: [] for body in self.simulator.physics_engine.bodies}
        
    def create_binary_star_system(self):
        """Create binary star system"""
        star1 = CelestialBody("Star 1", SUN_MASS, [-0.5 * AU, 0, 0], 
                             [0, 15000, 0], 20, '#FFD700', is_3d=True)
        star2 = CelestialBody("Star 2", SUN_MASS * 0.8, [0.5 * AU, 0, 0], 
                             [0, -15000, 0], 18, '#FFA500', is_3d=True)
        planet = CelestialBody("Planet", EARTH_MASS, [2 * AU, 0, 0.3 * AU], 
                              [0, 12000, 2000], 6, '#87CEEB', is_3d=True)
        
        self.simulator.physics_engine.bodies = [star1, star2, planet]
        self.simulator.trajectories = {body.name: [] for body in self.simulator.physics_engine.bodies}
        
    def start_simulation(self):
        """Start the simulation"""
        if self.simulator is None:
            self.create_scenario(self.scenario_var.get())
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # Start simulation in separate thread
        self.simulation_thread = threading.Thread(target=self.run_simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
    def pause_simulation(self):
        """Pause the simulation"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
    def reset_simulation(self):
        """Reset the simulation"""
        self.is_running = False
        self.create_scenario(self.scenario_var.get())
        self.update_visualization()
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
    def run_simulation_loop(self):
        """Run the simulation loop"""
        while self.is_running:
            if self.simulator:
                self.simulator.step()
                self.root.after(0, self.update_visualization)
                time.sleep(0.1 / self.speed_var.get())  # Adjust speed
                
    def update_visualization(self):
        """Update the visualization"""
        if self.simulator is None:
            return
            
        self.ax.clear()
        self.ax.set_facecolor('black')
        
        # Add starfield
        self.simulator._add_starfield(self.ax, True)
        
        # Plot trajectories if enabled
        if self.show_trajectories.get():
            for body_name, trajectory in self.simulator.trajectories.items():
                if len(trajectory) > 1:
                    recent_trajectory = trajectory[-500:]  # Limit for performance
                    trajectory_array = np.array(recent_trajectory)
                    trajectory_au = trajectory_array / AU
                    
                    traj_color = self.simulator._get_trajectory_color(body_name)
                    self.ax.plot(trajectory_au[:, 0], trajectory_au[:, 1], trajectory_au[:, 2],
                               alpha=0.6, linewidth=1, color=traj_color)
        
        # Plot bodies
        for body in self.simulator.physics_engine.bodies:
            pos_au = body.position / AU
            body_color, body_size = self.simulator._get_realistic_body_properties(body)
            
            if self.realistic_mode.get():
                self.simulator._plot_realistic_body_3d(self.ax, pos_au, body_color, body_size, body.name)
            else:
                self.ax.scatter(pos_au[0], pos_au[1], pos_au[2], 
                              s=body_size**2, c=body_color, alpha=0.9)
            
            # Add labels if enabled
            if self.show_labels.get():
                self.ax.text(pos_au[0], pos_au[1], pos_au[2], body.name, 
                           color='white', fontsize=8)
        
        # Set axis properties
        self.ax.set_xlabel('X Position (AU)', color='white')
        self.ax.set_ylabel('Y Position (AU)', color='white')
        self.ax.set_zlabel('Z Position (AU)', color='white')
        self.ax.set_title(f'🌌 Orbital Mechanics Simulator (t = {self.simulator.time/86400:.1f} days)', 
                         color='white', fontsize=12)
        
        # Set axis limits
        all_positions = [body.position / AU for body in self.simulator.physics_engine.bodies]
        if all_positions:
            positions_array = np.array(all_positions)
            max_coord = np.max(np.abs(positions_array)) * 1.2
            self.ax.set_xlim(-max_coord, max_coord)
            self.ax.set_ylim(-max_coord, max_coord)
            self.ax.set_zlim(-max_coord, max_coord)
        
        self.canvas.draw()
        
    def update_planet_info(self):
        """Update planet information display"""
        info_text = """🌌 Solar System Information

☀️ Sun
- Mass: 1.989 × 10³⁰ kg
- Temperature: 5,778 K
- Composition: 73% H, 25% He

🪐 Mercury
- Distance: 0.39 AU
- Period: 88 days
- Surface: Rocky, cratered

🪐 Venus  
- Distance: 0.72 AU
- Period: 225 days
- Atmosphere: CO₂, thick clouds

🌍 Earth
- Distance: 1.0 AU
- Period: 365 days
- Unique: Liquid water, life

🪐 Mars
- Distance: 1.52 AU
- Period: 687 days
- Features: Polar ice caps

🪐 Jupiter
- Distance: 5.2 AU
- Period: 12 years
- Great Red Spot storm

🪐 Saturn
- Distance: 9.58 AU
- Period: 29 years
- Famous for its rings

🪐 Uranus
- Distance: 19.2 AU
- Period: 84 years
- Tilted on its side

🪐 Neptune
- Distance: 30.1 AU
- Period: 165 years
- Strongest winds in solar system"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        
    def save_simulation(self):
        """Save current simulation state"""
        if self.simulator is None:
            messagebox.showwarning("Warning", "No simulation to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            # Save simulation data
            data = {
                'bodies': [],
                'time': self.simulator.time,
                'dt': self.simulator.dt
            }
            
            for body in self.simulator.physics_engine.bodies:
                body_data = {
                    'name': body.name,
                    'mass': body.mass,
                    'position': body.position.tolist(),
                    'velocity': body.velocity.tolist(),
                    'radius': body.radius,
                    'color': body.color,
                    'is_3d': body.is_3d
                }
                data['bodies'].append(body_data)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            messagebox.showinfo("Success", f"Simulation saved to {filename}")
            
    def load_simulation(self):
        """Load simulation from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Recreate bodies
                bodies = []
                for body_data in data['bodies']:
                    body = CelestialBody(
                        name=body_data['name'],
                        mass=body_data['mass'],
                        position=body_data['position'],
                        velocity=body_data['velocity'],
                        radius=body_data['radius'],
                        color=body_data['color'],
                        is_3d=body_data['is_3d']
                    )
                    bodies.append(body)
                
                # Create new simulator
                self.simulator = OrbitalSimulator(bodies, dt=data['dt'])
                self.simulator.time = data['time']
                
                messagebox.showinfo("Success", f"Simulation loaded from {filename}")
                self.update_visualization()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load simulation: {str(e)}")
                
    def export_animation(self):
        """Export animation as GIF"""
        if self.simulator is None:
            messagebox.showwarning("Warning", "No simulation to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        
        if filename:
            # This would require implementing animation export
            messagebox.showinfo("Info", "Animation export feature coming soon!")
            
    def export_data(self):
        """Export simulation data"""
        if self.simulator is None:
            messagebox.showwarning("Warning", "No simulation to export!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            # Export trajectory data
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Body', 'Time', 'X', 'Y', 'Z', 'VX', 'VY', 'VZ'])
                
                for body in self.simulator.physics_engine.bodies:
                    for i, pos in enumerate(self.simulator.trajectories[body.name]):
                        vel = body.velocity
                        writer.writerow([body.name, i * self.simulator.dt, 
                                       pos[0], pos[1], pos[2], vel[0], vel[1], vel[2]])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            

        
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """🌌 Orbital Mechanics Simulator - User Guide

Getting Started:
1. Select a scenario from the left panel
2. Adjust time step and speed controls
3. Click 'Start' to begin simulation
4. Use mouse to rotate 3D view
5. Use touchpad to zoom and pan

Features:
- Realistic planet appearances
- Interactive 3D visualization
- Multiple solar system scenarios
- Data export capabilities
- Educational planet information

Tips:
- Try different scenarios
- Adjust speed for different effects
- Enable/disable trajectories
- Use realistic mode for best appearance

For more help, visit the project documentation."""
        
        messagebox.showinfo("User Guide", guide_text)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """🌌 Orbital Mechanics Simulator
Interactive Edition

Version: 2.0
Created with Python, Tkinter, and Matplotlib

Features:
✓ Realistic 3D visualization
✓ Interactive controls
✓ Multiple scenarios
✓ Educational content
✓ Data export
✓ Professional tools

For professionals and space enthusiasts!"""
        
        messagebox.showinfo("About", about_text)

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = OrbitalMechanicsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
