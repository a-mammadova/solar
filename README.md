<<<<<<< HEAD
# Orbital Mechanics Simulator

A Python implementation of orbital mechanics with gravitational forces, featuring realistic physics simulation and visualization.

## Features

- **Realistic Physics**: Implements Newton's law of universal gravitation
- **Multiple Bodies**: Support for N-body gravitational interactions
- **Stable Integration**: Uses Verlet integration for accurate orbital mechanics
- **Visualization**: 2D plotting with trajectory tracking
- **Energy Conservation**: Tracks orbital energy and angular momentum
- **Customizable**: Easy to create custom celestial body systems


### Gravitational Force
The simulator implements Newton's law of universal gravitation:
```
F = G * m1 * m2 / r²
```

Where:
- G = 6.67430e-11 m³/kg/s² (gravitational constant)
- m1, m2 = masses of the two bodies
- r = distance between bodies


### Energy Conservation
The simulator tracks:
- **Kinetic Energy**: KE = ½mv²
- **Potential Energy**: PE = -GMm/r
- **Total Energy**: E = KE + PE


**Methods:**
- `step()`: Advance simulation by one time step
- `run_simulation(duration)`: Run simulation for specified duration
- `visualize()`: Create visualization of current state

## Physical Constants

The simulator uses real physical constants:
- Gravitational constant: G = 6.67430e-11 m³/kg/s²
- Astronomical unit: AU = 1.496e11 m
- Earth mass: 5.972e24 kg
- Sun mass: 1.989e30 kg
=======
# solar
a simulation like thing of solar system for students or enthusiasts
>>>>>>> 9781d7ac6368736bf30c6cfe2dabdce1ef7c3118
