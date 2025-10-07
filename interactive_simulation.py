"""
Interactive Orbital Mechanics Simulation
Real-time controls with pause, reset, speed adjustment, and live visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import threading
import time
from orbital_simulator import OrbitalSimulator, CelestialBody, SUN_MASS, EARTH_MASS, AU, G

class InteractiveSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("🌌 Interactive Orbital Mechanics Simulator")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#1a1a1a')
        
        # Simulation variables
        self.simulator = None
        self.is_running = False
        self.is_paused = False
        self.simulation_thread = None
        self.update_thread = None
        
        # Control variables
        self.speed_var = tk.DoubleVar(value=1.0)
        self.dt_var = tk.DoubleVar(value=1.0)
        self.show_trajectories = tk.BooleanVar(value=True)
        self.show_labels = tk.BooleanVar(value=True)
        self.realistic_mode = tk.BooleanVar(value=True)
        
        # Data tracking
        self.data_history = {
            'time': [],
            'positions': {},
            'energies': {}
        }
        
        self.create_widgets()
        self.create_simulation()
        
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Top menu to navigate across features
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        hub_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hub", menu=hub_menu)
        hub_menu.add_command(label="Open Main Hub", command=self.open_main_hub)
        hub_menu.add_separator()
        hub_menu.add_command(label="Interactive Simulation", command=lambda: None)
        hub_menu.add_command(label="Educational Features", command=self.open_educational_features)
        hub_menu.add_command(label="Educational Quiz", command=self.open_educational_quiz)
        hub_menu.add_command(label="Realistic Solar System Demo", command=self.open_realistic_demo)
        hub_menu.add_command(label="Professional Features", command=self.open_professional_features)
        hub_menu.add_command(label="Planet Data Analyzer", command=self.open_planet_analyzer)

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel - Visualization
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_control_panel(left_panel)
        self.create_visualization_panel(right_panel)
        
    def create_control_panel(self, parent):
        """Create the control panel"""
        # Title
        title_label = ttk.Label(parent, text="🌌 Simulation Controls", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Simulation Controls
        sim_frame = ttk.LabelFrame(parent, text="Simulation Controls", padding=10)
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="▶ Start", 
                                     command=self.start_simulation, width=12)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_button = ttk.Button(button_frame, text="⏸ Pause", 
                                      command=self.pause_simulation, 
                                      state=tk.DISABLED, width=12)
        self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reset_button = ttk.Button(button_frame, text="🔄 Reset", 
                                      command=self.reset_simulation, width=12)
        self.reset_button.pack(side=tk.LEFT)
        
        # Speed control
        ttk.Label(sim_frame, text="Simulation Speed:").pack(anchor=tk.W)
        speed_scale = ttk.Scale(sim_frame, from_=0.1, to=10.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, command=self.on_speed_change)
        speed_scale.pack(fill=tk.X, pady=(0, 5))
        
        self.speed_label = ttk.Label(sim_frame, text="Speed: 1.0x")
        self.speed_label.pack(anchor=tk.W)
        
        # Time step control
        ttk.Label(sim_frame, text="Time Step (hours):").pack(anchor=tk.W)
        dt_scale = ttk.Scale(sim_frame, from_=0.1, to=24.0, variable=self.dt_var, 
                            orient=tk.HORIZONTAL, command=self.on_dt_change)
        dt_scale.pack(fill=tk.X, pady=(0, 5))
        
        self.dt_label = ttk.Label(sim_frame, text="Time Step: 1.0 hours")
        self.dt_label.pack(anchor=tk.W)
        
        # Visualization Options
        vis_frame = ttk.LabelFrame(parent, text="Visualization Options", padding=10)
        vis_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(vis_frame, text="Show Trajectories", 
                       variable=self.show_trajectories, 
                       command=self.update_visualization).pack(anchor=tk.W)
        
        ttk.Checkbutton(vis_frame, text="Show Planet Labels", 
                       variable=self.show_labels, 
                       command=self.update_visualization).pack(anchor=tk.W)
        
        ttk.Checkbutton(vis_frame, text="Realistic Appearance", 
                       variable=self.realistic_mode, 
                       command=self.update_visualization).pack(anchor=tk.W)
        
        # Scenario Selection
        scenario_frame = ttk.LabelFrame(parent, text="Scenarios", padding=10)
        scenario_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.scenario_var = tk.StringVar(value="Complete Solar System")
        scenarios = [
            "Complete Solar System",
            "Inner Planets Only",
            "Gas Giants Only",
            "Earth-Moon System",
            "Binary Star System"
        ]
        
        for scenario in scenarios:
            ttk.Radiobutton(scenario_frame, text=scenario, variable=self.scenario_var, 
                           value=scenario, command=self.on_scenario_change).pack(anchor=tk.W)
        
        # Status Information
        status_frame = ttk.LabelFrame(parent, text="Simulation Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, width=30, wrap=tk.WORD, 
                                  bg='#2a2a2a', fg='white', font=('Arial', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Update status
        self.update_status()

    def open_main_hub(self):
        try:
            subprocess.Popen([sys.executable, "main_hub.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Main Hub: {e}")

    def open_educational_features(self):
        try:
            subprocess.Popen([sys.executable, "educational_quiz_gui.py"])  # includes features hub
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Educational Features: {e}")

    def open_educational_quiz(self):
        try:
            subprocess.Popen([sys.executable, "educational_quiz_gui.py"])  # opens quiz window
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Educational Quiz: {e}")

    def open_realistic_demo(self):
        try:
            subprocess.Popen([sys.executable, "realistic_solar_system_demo.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Realistic Demo: {e}")

    def open_professional_features(self):
        try:
            subprocess.Popen([sys.executable, "professional_features.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Professional Features: {e}")

    def open_planet_analyzer(self):
        try:
            subprocess.Popen([sys.executable, "planet_data_analyzer.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Planet Data Analyzer: {e}")
        
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
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        
    def create_simulation(self):
        """Create the initial simulation"""
        self.simulator = OrbitalSimulator([], dt=self.dt_var.get() * 3600)
        self.create_scenario(self.scenario_var.get())
        self.update_visualization()
        
    def create_scenario(self, scenario_name):
        """Create the selected scenario"""
        if scenario_name == "Complete Solar System":
            self.simulator.create_realistic_space_scene()
        elif scenario_name == "Inner Planets Only":
            self.create_inner_planets()
        elif scenario_name == "Gas Giants Only":
            self.create_gas_giants()
        elif scenario_name == "Earth-Moon System":
            self.create_earth_moon_system()
        elif scenario_name == "Binary Star System":
            self.create_binary_star_system()
        
        # Initialize data history
        self.data_history = {
            'time': [],
            'positions': {},
            'energies': {}
        }
        
        for body in self.simulator.physics_engine.bodies:
            self.data_history['positions'][body.name] = []
            self.data_history['energies'][body.name] = []
    
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
            self.create_simulation()
        
        self.is_running = True
        self.is_paused = False
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.run_simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
    def pause_simulation(self):
        """Pause/resume the simulation"""
        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="⏸ Pause")
        else:
            self.is_paused = True
            self.pause_button.config(text="▶ Resume")
    
    def reset_simulation(self):
        """Reset the simulation"""
        self.is_running = False
        self.is_paused = False
        
        # Wait for threads to finish
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1)
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        
        # Reset simulation
        self.create_simulation()
        self.update_visualization()
        
        # Reset buttons
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
        
    def run_simulation_loop(self):
        """Run the simulation loop"""
        while self.is_running:
            if not self.is_paused:
                if self.simulator:
                    self.simulator.step()
                    
                    # Record data
                    self.data_history['time'].append(self.simulator.time)
                    for body in self.simulator.physics_engine.bodies:
                        self.data_history['positions'][body.name].append(body.position.copy())
                        energy = self.simulator.physics_engine.get_orbital_energy(body)
                        self.data_history['energies'][body.name].append(energy)
                
                # Adjust speed
                time.sleep(0.1 / self.speed_var.get())
            else:
                time.sleep(0.1)
    
    def update_loop(self):
        """Update visualization loop"""
        while self.is_running:
            self.root.after(0, self.update_visualization)
            self.root.after(0, self.update_status)
            time.sleep(0.1)  # Update every 100ms
    
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
                    recent_trajectory = trajectory[-1000:]  # Limit for performance
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
        
        # Dynamic title
        status = "Running" if self.is_running and not self.is_paused else "Paused" if self.is_paused else "Stopped"
        self.ax.set_title(f'🌌 Interactive Simulation - {status} (t = {self.simulator.time/86400:.1f} days)', 
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
    
    def update_status(self):
        """Update status information"""
        if self.simulator is None:
            return
        
        # Clear and update status text
        self.status_text.delete(1.0, tk.END)
        
        status_info = f"🌌 Simulation Status\n"
        status_info += f"{'='*25}\n\n"
        
        status_info += f"Time: {self.simulator.time/86400:.2f} days\n"
        status_info += f"Speed: {self.speed_var.get():.1f}x\n"
        status_info += f"Time Step: {self.dt_var.get():.1f} hours\n"
        status_info += f"Bodies: {len(self.simulator.physics_engine.bodies)}\n\n"
        
        status_info += f"Planet Positions (AU):\n"
        for body in self.simulator.physics_engine.bodies:
            if body.name == "Sun":
                continue
            pos_au = body.position / AU
            distance = np.linalg.norm(pos_au)
            status_info += f"  {body.name}: {distance:.3f} AU\n"
        
        status_info += f"\nPlanet Speeds (km/s):\n"
        for body in self.simulator.physics_engine.bodies:
            if body.name == "Sun":
                continue
            speed = np.linalg.norm(body.velocity) / 1000
            status_info += f"  {body.name}: {speed:.1f} km/s\n"
        
        # Energy conservation
        if len(self.data_history['time']) > 1:
            total_energy = sum(self.data_history['energies'][body.name][-1] 
                             for body in self.simulator.physics_engine.bodies)
            status_info += f"\nTotal Energy: {total_energy:.2e} J\n"
        
        self.status_text.insert(1.0, status_info)
    
    def on_speed_change(self, value):
        """Handle speed change"""
        self.speed_label.config(text=f"Speed: {self.speed_var.get():.1f}x")
    
    def on_dt_change(self, value):
        """Handle time step change"""
        self.dt_label.config(text=f"Time Step: {self.dt_var.get():.1f} hours")
        if self.simulator:
            self.simulator.dt = self.dt_var.get() * 3600
    
    def on_scenario_change(self):
        """Handle scenario change"""
        if not self.is_running:
            self.create_scenario(self.scenario_var.get())
            self.update_visualization()
        else:
            messagebox.showwarning("Warning", "Please reset simulation before changing scenario!")

def main():
    """Main function to run the interactive simulation"""
    root = tk.Tk()
    app = InteractiveSimulation(root)
    
    # Handle window closing
    def on_closing():
        app.is_running = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
