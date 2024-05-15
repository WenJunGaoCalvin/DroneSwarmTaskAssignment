from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, ConstraintList, minimize, NonNegativeIntegers
import numpy as np
import math
import time

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

def calc_profit(V,W,p,assignment):
    # lower score is better
    m = len(W)
    n = len(V)
    total_profit = 0
    for j in range(n):
        sub_profit = V[j]
        for i in range(m):

            sub_profit *= (1-p[i][j])**assignment[i][j]
        total_profit += sub_profit
    
    # profit2 = sum(V[j-1] * np.prod([(1 - p[i-1][j-1]) ** assignment[i-1][j-1] for i in range(1, m+1)]) for j in range(1, n+1))
    # print("checking profit")
    # print(profit2)
    # print(total_profit)
    return total_profit

def weapon_target_assignment(V, W, p, timeout):
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
    solver.options['max_cpu_time'] = timeout
    
    # Solve the optimization problem
    solver.solve(model, tee=False)

    # Extract the solution
    assignment = np.round(np.array([[model.x[i, j]() for j in range(1, n+1)] for i in range(1, m+1)]))
    
    obj = calc_profit(V, W, p, assignment)
    # obj2 = sum(V[j-1] * np.prod([(1 - p[i-1, j-1]) ** assignment[i-1,j-1] for i in range(1, m+1)]) for j in range(1, n+1))
    # print("obj2: ", obj2)
    return assignment.astype(int), obj #model.obj()
    # output: assignment of a specific chaser platform to every target (rows), 
    # value represents no. of that chaser platform

def greedy_WTA(V,W,p,timeout):
    m = len(W)
    n = len(V)
    assignment = np.zeros((m,n))
    start = time.perf_counter()
    for i in range(m): # iterate through W
        N = W[i]
        for k in range(N):
            profits = np.zeros(n)
            for j in range(n):
                profit = V[j]*(p[i][j])
                for a in range(m):
                    profit *= (1-p[a][j])**assignment[a][j]
                profits[j] = profit
            max_ind = np.argmax(profits)
            assignment[i][max_ind] +=1
            
            check = time.perf_counter()
            time_check = check - start
            if time_check >= timeout:
                print("Warning: Time exceeded timeout threshold for Greedy WTA.")
                score = calc_profit(V, W, p, assignment)
                return assignment, score

    score = calc_profit(V, W, p, assignment)
    return assignment, score
    # output: assignment of a specific chaser platform to every target (rows), 
    # value represents no. of that chaser platform
    
def task_assignment(V,W, theta_is, theta_ts, vis, vts, ds):
    p = generate_probs(theta_is, theta_ts, vis, vts, ds)
    print("Probabilities:", p)
    return weapon_target_assignment(V, W, p, timeout)



def getWays(num, n):
    # find all possible ways to sum up a subset of numbers to get target
    
    def subset_sum(n, target, all_ways, partial=[]):
        if target == 0 and n == 0:
            # print(partial)
            all_ways.append(partial)
            return
        elif target < 0 or n == 0:
            return
        else:
            for i in range(target+1):
                copy = partial.copy()
                copy.append(i)
                subset_sum(n-1, target-i, all_ways, copy)
    all_ways=[]
    target = num
    subset_sum(n, target, all_ways)
    return all_ways

def get_best(V,W,p,assignments,start,timeout):
    # get best assignment
    best_assignment = assignments[0]
    best_score = calc_profit(V,W,p,best_assignment)
    for assignment in assignments:
        score = calc_profit(V,W,p,assignment)
        if score < best_score:
            best_assignment = assignment
            best_score = score
        check = time.perf_counter()
        time_check = check - start
        if time_check >= timeout:
            print("Warning: Time exceeded timeout threshold for Brute Force WTA.")
            return np.array(best_assignment), best_score
    return np.array(best_assignment), best_score
            
def brute_force_WTA(V,W,p,timeout):
    m = len(W)
    n = len(V)
    best_assignment = []
    assignments_by_inter = []
    start = time.perf_counter()
    for i in range(m): # iterate through W
        N = W[i]
        assignments_by_inter.append(getWays(N, n))
        
    # convert assignments_by_inter to assignments
    x = 1 #for checking if all combis are accounted for
    for elem in assignments_by_inter:
        k = len(elem)
        x *= k
    assignments = []
    if len(assignments_by_inter) == 1:
        assignments = [[arr] for arr in assignments_by_inter[0]]
    else:
        indices = [0 for i in range(m)]
        while 1:
            assignment = []
            for i in range(m):
                assignment.append(assignments_by_inter[i][indices[i]])
            assignments.append(assignment)
            nxt = m-1
            while(nxt >= 0 and indices[nxt]+1 >=len(assignments_by_inter[nxt])):
                nxt -= 1
            if (nxt < 0):
                break
            indices[nxt] +=1
            for i in range(nxt+1,m):
                indices[i] = 0
            
            check = time.perf_counter()
            time_check = check - start
            if time_check >= timeout:
                print("Warning: Time exceeded timeout threshold for Brute Force WTA.")
                best_assignment, best_score = get_best(V,W,p,assignments,start,timeout)
                return np.array(best_assignment), best_score
    # if len(assignments) == x:
        # print("All combinations accounted for")
        # print(x)

    best_assignment, best_score = get_best(V,W,p,assignments,start,timeout)
    return np.array(best_assignment), best_score

""" Example usage fot WTA Algorithm"""
if __name__ == "__main__":
    timeout = 120
    V = [1, 1, 1, 1]
    W = [1,1,1,1,1]
    p = np.array([[0.99, 0, 0.1, 0.01],[0.99, 0, 0.1, 0.01],[0.99, 0, 0.1, 0.01],[0.99, 0, 0.1, 0.01],[0.99, 0, 0.1, 0.01]])
    
    
    result1 = weapon_target_assignment(V, W, p, timeout)
    greedy1 = greedy_WTA(V, W, p, timeout)
    brute1 = brute_force_WTA(V, W, p,timeout)
    print("Example 1:\nWTA Assignment:", result1[0], "\nObjective Value:", result1[1])
    print("\nGreedy Assignment:", greedy1[0], "\nObjective Value:", greedy1[1])
    print("\nBrute Force Assignment:", brute1[0], "\nObjective Value:", brute1[1])
    
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
    
    result2 = weapon_target_assignment(V, W, p, timeout)
    greedy2 = greedy_WTA(V, W, p, timeout)
    brute2 = brute_force_WTA(V, W, p,timeout)
    print("\nExample 2:\nAssignment:", result2[0], "\nObjective Value:", result2[1])
    print("\nGreedy Assignment:", greedy2[0], "\nObjective Value:", greedy2[1])
    print("\nBrute Force Assignment:", brute2[0], "\nObjective Value:", brute2[1])
    
    V = [16, 29, 43, 43]
    W = [6, 6, 7, 6]
    p = np.array([
        [0.36, 0.71, 0.96, 0.91],
        [0.96, 0.25, 0.79, 0.68],
        [0.75, 0.14, 0.23, 1.  ],
        [1, 0.43, 0.31, 0.97]
    ])
    
    result3 = weapon_target_assignment(V, W, p, timeout)
    greedy3 = greedy_WTA(V, W, p, timeout)
    # brute3 = brute_force_WTA(V, W, p)
    print("\nExample 3:\nAssignment:", result3[0], "\nObjective Value:", result3[1])
    print("\nGreedy Assignment:", greedy3[0], "\nObjective Value:", greedy3[1])
    # print("\nBrute Force Assignment:", brute3[0], "\nObjective Value:", brute3[1])
    
    V = [7, 2]
    W = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    p = np.array([[0.85, 0.22],
     [0.32, 0.85],
     [0.88, 0.14],
     [0.42, 0.3 ],
     [0.27, 0.23],
     [0.48, 0.78],
     [1.  , 1.  ],
     [0.57, 0.96],
     [0.04, 0.75],
     [0.83, 0.86]])
    
    result4 = weapon_target_assignment(V, W, p, timeout)
    greedy4 = greedy_WTA(V, W, p, timeout)
    brute4 = brute_force_WTA(V, W, p,timeout)
    print("\nExample 4:\nAssignment:", result4[0], "\nObjective Value:", result4[1])
    print("\nGreedy Assignment:", greedy4[0], "\nObjective Value:", greedy4[1])
    print("\nBrute Force Assignment:", brute4[0], "\nObjective Value:", brute4[1])
    
    
    """ Example with kinematic inputs 
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
    """
    
