# DroneSwarmTaskAssignment
### Motivation
With the increasing threat of hostile drone swarms, there needs to be a solution to neutralise these threats. One of such solutions is the use of a group of drone interceptors. These interceptors require a task assignment procedure, telling each interceptor which hostile drone should target. This algorithm should thus coordinate the interceptor drones and enhance their defence capabilities.

### Weapon Target Assignment
The algorithm is based on the weapon task assignment algorithm.
https://en.wikipedia.org/wiki/Weapon_target_assignment_problem

The algorithm consists of 3 parameters: 
1. Threat/priority value of a target
2. Probability of destruction of a target by a specific weapon 
3. The available number of each weapon type

The first 2 parameters are difficult to determine as many factors could affect them. The aim of this project is to decompose the first 2 parameters into measureable quantities.
