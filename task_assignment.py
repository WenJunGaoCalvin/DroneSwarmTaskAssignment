from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, ConstraintList, minimize, NonNegativeIntegers
import numpy as np
import math

# p: probability of destruction
# W: friendlies, value represents number of this platform of chasers
# V: threats, higher the value, the higher the priority

def heading_adv(theta_i, theta_t):
    if abs(theta_i) < math.pi/2 and abs(theta_t) < math.pi/2:
        # assuming head on orientation, values should cancel each other if the 
        # angles are on the same side of LOS
        Dtheta = 1-abs(theta_i-theta_t)/math.pi
    else:
        Dtheta = 0.001
    return Dtheta

def vel_adv(vi,vt):
    if vi>vt:
        Dv = 1
    elif 0.5*vt<=vi and vi<vt:
        Dv = vi/vt
    elif vi<0.5*vt:
        Dv = 0.1
    else:
        print("Velocity advantage calculation error: case not considered")
    return Dv

def dist_adv(d):
    d0 = 0 # threshold for distance, below this means low advantage
    Dd = 2/(1+math.exp(d-d0))
    return Dd

def overall_adv(Dd,Dv,Dtheta):
    lambda1 = 0.5
    lambda2 = 0.4
    lambda3 = 0.1
    D = lambda1*Dd + lambda2*Dv + lambda3*Dtheta
    return D

def generate_probs(theta_is, theta_ts, vis, vts, ds):
    # all inputs: columns = num of targets, rows = num of interceptor types
    m = theta_is.shape[0]
    n = theta_is.shape[1]
    p = np.empty([m,n])
    for i in range(m):
        for j in range(n):
            Dd = dist_adv(ds[i,j])
            Dv = vel_adv(vis[i], vts[j])
            Dtheta = heading_adv(theta_is[i,j], theta_ts[i,j])
            p[i,j] = overall_adv(Dd,Dv,Dtheta)
    return p

def weapon_target_assignment(V, W, p):
    m = len(W)
    n = len(V)

    # Create a concrete optimization model
    model = ConcreteModel()

    # Define decision variables
    model.x = Var(range(1, m+1), range(1, n+1), within=NonNegativeIntegers)

    # Define the objective function
    model.obj = Objective(expr=sum(V[j-1] * np.prod([(1 - p[i-1, j-1]) ** model.x[i, j] for i in range(1, m+1)]) for j in range(1, n+1)), sense=minimize)

    # Define constraints
    model.constraints = ConstraintList()
    for i in range(1, m+1):
        model.constraints.add(sum(model.x[i, j] for j in range(1, n+1)) <= W[i-1])

    # Create the solver
    solver = SolverFactory('ipopt')
    
    # Solve the optimization problem
    solver.solve(model, tee=False)

    # Extract the solution
    assignment = np.round(np.array([[model.x[i, j]() for j in range(1, n+1)] for i in range(1, m+1)]))
    
    return assignment.astype(int), model.obj()
    # output: assignment of a specific chaser platform to every target (rows), 
    # value represents no. of that chaser platform
    
def task_assignment(V,W, theta_is, theta_ts, vis, vts, ds):
    p = generate_probs(theta_is, theta_ts, vis, vts, ds)
    print("Probabilities:", p)
    return weapon_target_assignment(V, W, p)

""" Example usage fot WTA Algorithm"""


V = [1, 1, 1, 1]
W = [5]
p = np.array([[0.99, 0, 0.1, 0.01]])


result1 = weapon_target_assignment(V, W, p)
print("Example 1:\nAssignment:", result1[0], "\nObjective Value:", result1[1])

# Analysis: This algorithm will give up on intercepting targets with a low 
# corresponding p value

V = [5, 10, 20]
W = [5, 2, 1]
# p: columns = num of targets, rows = num of interceptor types
p = np.array([
    [0.3, 0.2, 0.5],
    [0.1, 0.6, 0.5],
    [0.4, 0.5, 0.4]
])

result2 = weapon_target_assignment(V, W, p)
print("\nExample 2:\nAssignment:", result2[0], "\nObjective Value:", result2[1])

V = [5, 10, 20]
W = [20]
p = np.array([
    [0.3, 0.2, 0.5]
])

result3 = weapon_target_assignment(V, W, p)
print("\nExample 3:\nAssignment:", result3[0], "\nObjective Value:", result3[1])


""" Example with kinematic inputs """
# inputs: columns = num of targets, rows = num of interceptor types

# angle of interceptors with LOSs (cc as +ve)
theta_is = np.array([[0,0],
                     [0,0]])

# angle of friendlies with LOSs (cc as -ve)
theta_ts = np.array([[0,0],
                     [0.1,0.9]])

# velocity of interceptors
vis = [2,5]

# velocity of targets
vts = [1,6]

# distance between interceptors and targets
ds = np.array([[10,10],
               [8,8]])

V = [5, 10]
W = [2,3]

print("\nExample 4: ")
result4 = task_assignment(V,W, theta_is, theta_ts, vis, vts, ds)
print("Assignment:", result4[0], "\nObjective Value:", result4[1])
