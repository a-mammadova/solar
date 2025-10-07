"""
Real-Time Planet Data Monitor
Live monitoring of planet data during simulation
"""

from orbital_simulator import OrbitalSimulator, CelestialBody, SUN_MASS, EARTH_MASS, AU, G
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

class RealTimeMonitor:
    def __init__(self):
        self.simulator = None
        self.monitoring = False
        self.data_history = {
            'time': [],
            'positions': {},
            'velocities': {},
            'energies': {}
        }
        
    def create_solar_system(self):
        """Create solar system for monitoring"""
        self.simulator = OrbitalSimulator([], dt=3600.0)
        self.simulator.create_realistic_space_scene()
        
        # Initialize data history
        for body in self.simulator.physics_engine.bodies:
            self.data_history['positions'][body.name] = []
            self.data_history['velocities'][body.name] = []
            self.data_history['energies'][body.name] = []
        
        return self.simulator
    
    def start_monitoring(self, duration_hours=24):
        """Start real-time monitoring"""
        print(f"🔍 Starting Real-Time Monitoring for {duration_hours} hours")
        print("=" * 55)
        
        if self.simulator is None:
            self.create_solar_system()
        
        self.monitoring = True
        start_time = time.time()
        
        print("Monitoring planet data...")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while self.monitoring and (time.time() - start_time) < duration_hours * 3600:
                # Record current data
                current_time = self.simulator.time
                self.data_history['time'].append(current_time)
                
                for body in self.simulator.physics_engine.bodies:
                    # Position (in AU)
                    pos_au = body.position / AU
                    self.data_history['positions'][body.name].append(pos_au.copy())
                    
                    # Velocity (in km/s)
                    vel_kms = body.velocity / 1000
                    self.data_history['velocities'][body.name].append(vel_kms.copy())
                    
                    # Energy
                    energy = self.simulator.physics_engine.get_orbital_energy(body)
                    self.data_history['energies'][body.name].append(energy)
                
                # Step simulation
                self.simulator.step()
                
                # Print current status every hour
                if len(self.data_history['time']) % 3600 == 0:  # Every hour
                    self.print_current_status()
                
                # Small delay for real-time effect
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            self.monitoring = False
        
        print(f"\n✅ Monitoring completed!")
        print(f"   - Recorded {len(self.data_history['time'])} data points")
        print(f"   - Duration: {self.simulator.time/86400:.1f} days")
        
        return self.data_history
    
    def print_current_status(self):
        """Print current planet status"""
        current_time = self.simulator.time / 86400  # Convert to days
        
        print(f"\n📊 Status at {current_time:.1f} days:")
        print("-" * 40)
        
        for body in self.simulator.physics_engine.bodies:
            if body.name == "Sun":
                continue
                
            pos_au = body.position / AU
            vel_kms = body.velocity / 1000
            distance = np.linalg.norm(pos_au)
            speed = np.linalg.norm(vel_kms)
            
            print(f"{body.name}:")
            print(f"  Distance: {distance:.3f} AU")
            print(f"  Speed: {speed:.1f} km/s")
            print(f"  Position: [{pos_au[0]:.3f}, {pos_au[1]:.3f}, {pos_au[2]:.3f}] AU")
    
    def plot_monitoring_data(self):
        """Plot the monitoring data"""
        if not self.data_history['time']:
            print("No data to plot!")
            return
        
        print("\n📊 Creating monitoring plots...")
        
        # Convert time to days
        times_days = np.array(self.data_history['time']) / 86400
        
        # Create plots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10), facecolor='black')
        
        # Plot 1: Distances from Sun
        ax1.set_facecolor('black')
        ax1.set_title('Planet Distances from Sun', color='white', fontsize=14)
        ax1.set_xlabel('Time (days)', color='white')
        ax1.set_ylabel('Distance (AU)', color='white')
        ax1.tick_params(colors='white')
        
        for body_name, positions in self.data_history['positions'].items():
            if body_name == "Sun":
                continue
            distances = [np.linalg.norm(pos) for pos in positions]
            ax1.plot(times_days, distances, label=body_name, linewidth=2)
        
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Orbital speeds
        ax2.set_facecolor('black')
        ax2.set_title('Planet Orbital Speeds', color='white', fontsize=14)
        ax2.set_xlabel('Time (days)', color='white')
        ax2.set_ylabel('Speed (km/s)', color='white')
        ax2.tick_params(colors='white')
        
        for body_name, velocities in self.data_history['velocities'].items():
            if body_name == "Sun":
                continue
            speeds = [np.linalg.norm(vel) for vel in velocities]
            ax2.plot(times_days, speeds, label=body_name, linewidth=2)
        
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Energy conservation
        ax3.set_facecolor('black')
        ax3.set_title('Energy Conservation', color='white', fontsize=14)
        ax3.set_xlabel('Time (days)', color='white')
        ax3.set_ylabel('Total Energy (J)', color='white')
        ax3.tick_params(colors='white')
        
        total_energies = []
        for i in range(len(times_days)):
            total_energy = sum(self.data_history['energies'][body_name][i] 
                             for body_name in self.data_history['energies'].keys())
            total_energies.append(total_energy)
        
        ax3.plot(times_days, total_energies, 'r-', linewidth=2, label='Total Energy')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Earth's orbit (X vs Y)
        ax4.set_facecolor('black')
        ax4.set_title("Earth's Orbit", color='white', fontsize=14)
        ax4.set_xlabel('X Position (AU)', color='white')
        ax4.set_ylabel('Y Position (AU)', color='white')
        ax4.tick_params(colors='white')
        
        if 'Earth' in self.data_history['positions']:
            earth_positions = self.data_history['positions']['Earth']
            x_pos = [pos[0] for pos in earth_positions]
            y_pos = [pos[1] for pos in earth_positions]
            ax4.plot(x_pos, y_pos, 'b-', linewidth=2, label="Earth's Orbit")
            ax4.scatter(x_pos[0], y_pos[0], c='green', s=100, label='Start')
            ax4.scatter(x_pos[-1], y_pos[-1], c='red', s=100, label='End')
        
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_aspect('equal')
        
        plt.tight_layout()
        plt.show()
    
    def export_monitoring_data(self, filename="monitoring_data"):
        """Export monitoring data"""
        print(f"\n💾 Exporting monitoring data to {filename}...")
        
        # Prepare data for export
        export_data = {
            'monitoring_info': {
                'start_time': datetime.now().isoformat(),
                'duration_days': self.simulator.time / 86400,
                'data_points': len(self.data_history['time']),
                'time_step': self.simulator.dt
            },
            'time_series': {
                'times_days': [t / 86400 for t in self.data_history['time']],
                'planets': {}
            }
        }
        
        # Add planet data
        for body_name in self.data_history['positions'].keys():
            if body_name == "Sun":
                continue
                
            planet_data = {
                'positions_au': self.data_history['positions'][body_name],
                'velocities_kms': self.data_history['velocities'][body_name],
                'energies_j': self.data_history['energies'][body_name]
            }
            export_data['time_series']['planets'][body_name] = planet_data
        
        # Save to JSON
        import json
        with open(f"{filename}.json", 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Monitoring data exported to {filename}.json")
        return export_data
    
    def quick_data_check(self):
        """Quick check of current planet data"""
        if self.simulator is None:
            self.create_solar_system()
        
        print("🔍 QUICK DATA CHECK")
        print("=" * 25)
        
        print(f"Simulation Time: {self.simulator.time/86400:.2f} days")
        print(f"Time Step: {self.simulator.dt/3600:.1f} hours")
        print(f"Bodies: {len(self.simulator.physics_engine.bodies)}")
        
        print(f"\nCurrent Planet Positions (AU):")
        for body in self.simulator.physics_engine.bodies:
            if body.name == "Sun":
                continue
            pos_au = body.position / AU
            distance = np.linalg.norm(pos_au)
            print(f"  {body.name}: {distance:.3f} AU at [{pos_au[0]:.3f}, {pos_au[1]:.3f}, {pos_au[2]:.3f}]")
        
        print(f"\nCurrent Planet Speeds (km/s):")
        for body in self.simulator.physics_engine.bodies:
            if body.name == "Sun":
                continue
            speed = np.linalg.norm(body.velocity) / 1000
            print(f"  {body.name}: {speed:.1f} km/s")

def main():
    """Main function to demonstrate real-time monitoring"""
    print("🔍 Real-Time Planet Data Monitor")
    print("=" * 35)
    
    monitor = RealTimeMonitor()
    
    # Create solar system
    monitor.create_solar_system()
    
    # Quick data check
    monitor.quick_data_check()
    
    # Start monitoring (short duration for demo)
    print("\nStarting 1-hour monitoring demo...")
    data = monitor.start_monitoring(duration_hours=1)
    
    # Plot results
    monitor.plot_monitoring_data()
    
    # Export data
    monitor.export_monitoring_data("demo_monitoring")

if __name__ == "__main__":
    main()
