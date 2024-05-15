# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 15:22:51 2024

@author: Asus
"""
# p: probability of destruction
# W: friendlies, value represents number of this platform of chasers
# V: threats, higher the value, the higher the priority

from task_assignment import weapon_target_assignment, greedy_WTA, brute_force_WTA
from random import randint
import numpy as np
import csv
import pandas as pd
import time
import os

def generate_test_case(num_interceptor_platforms, num_targets, W_lims, V_lims, BF_FLAG):
    W = [0 for i in range(num_interceptor_platforms)]
    V = [0 for i in range(num_targets)]
    while 1:
        # test case will only be used if number of interceptors >= number of targets
        for i in range(num_interceptor_platforms):
            W[i] = randint(W_lims[0],W_lims[1])
        
        for i in range(num_targets):
            V[i] = randint(V_lims[0],V_lims[1])
        if sum(W) >= len(V):
            break
    threshold = len(V)
    if BF_FLAG and sum(W) > threshold:
        # if brute force method is used, limit number of players in scenario
        tmp = [elem/(sum(W)/threshold) for elem in W]
        W = [round(elem) for elem in tmp]

    m = len(W)
    n = len(V)
    p = np.zeros((m,n))
    for i in range(m):
        for j in range(n):
            p[i][j] = randint(0,100)/100
    return V, W, p

def reformat_assignment(num_targets, num_int, x,V, W, p, score,times):
    rank = num_int*1000 + num_targets
    interceptors_deployed = []
    solver_is_unfeasible = []
    for assignment in x:
        try:
            deployed = sum(sum(assignment))
            interceptors_deployed.append(deployed)
            if deployed > sum(W):
                solver_is_unfeasible.append(1)
            else:
                solver_is_unfeasible.append(0)
        except:
            interceptors_deployed.append("NA")
            solver_is_unfeasible.append(0)
            
    reformatted_x = [str(rank), str(num_int), str(num_targets),str(interceptors_deployed), str(V), str(W), str(p)]
    reformatted_x += [str(assignment) for assignment in x]
    reformatted_x += [str(e) for e in score]
    reformatted_x += [str(b) for b in solver_is_unfeasible]
    reformatted_x += [str(t) for t in times]
    return reformatted_x

def run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG, GREEDY_FLAG, BF_FLAG, timeout):
    # loop for each test case
    for i in range(int(num_tests)):
    #     V = [5, 10, 20]
    #     W = [5, 2, 1]
    #     # p: columns = num of targets, rows = num of interceptor types
    #     p = np.array([
    #         [0.3, 0.2, 0.5],
    #         [0.1, 0.6, 0.5],
    #         [0.4, 0.5, 0.4]
    #     ])
        num_interceptor_platforms = randint(num_interceptor_platforms_range[0],num_interceptor_platforms_range[1])
        num_targets= randint(num_targets_range[0],num_targets_range[1])            
        V, W, p = generate_test_case(num_interceptor_platforms, num_targets, W_lims, V_lims, BF_FLAG)
        print("Test Case {} with {} targets and {} interceptors".format(i,len(V), sum(W)))
        assignment = []
        score = []
        times = []
        tic1 = time.perf_counter()
        if WTA_FLAG:
            try:
                result1 = weapon_target_assignment(V, W, p, timeout)
            except:
                print("WTA Solver failed for no. of targets: ", len(V))
                result1 = ("WTA Solver Error","WTA Solver Error")
            toc1 = time.perf_counter()
            t_wta = toc1 - tic1
            print("WTA took {}s".format(t_wta))
            assignment.append(result1[0])
            score.append(result1[1])
            times.append(t_wta)
        if GREEDY_FLAG:
            tic2 = time.perf_counter()
            greedy1 = greedy_WTA(V, W, p, timeout)
            toc2 = time.perf_counter()
            t_greedy = toc2 - tic2
            print("Greedy took {}s".format(t_greedy))
            assignment.append(greedy1[0])
            score.append(greedy1[1])
            times.append(t_greedy)
        if BF_FLAG:
            tic3 = time.perf_counter()
            brute1 = brute_force_WTA(V, W, p, timeout)
            toc3 = time.perf_counter()
            t_brute = toc3 - tic3
            print("Brute Force took {}s".format(t_brute))
            assignment.append(brute1[0])
            score.append(brute1[1])
            times.append(t_brute)
        reformatted = reformat_assignment(num_targets, num_interceptor_platforms, assignment,V, W, p, score,times)
        datalog.append(reformatted)
        if not(i%100):
            print("Test Case {} complete".format(i))

# initialise main dataframes
assignments = []
datalog = []
timeout = 60

BF_TEST_FLAG = 1
FIND_NUM_TARGET_FLAG = 0
MAIN_TEST_FLAG = 0
V_TEST_FLAG = 0

# run test in batches and save in a folder
file_path = "C:\\Users\Asus\\OneDrive - National University of Singapore\\FYP\\Task Assignment\\results\\"
num = "with_bf" #len([name for name in os.listdir(file_path)])
if not os.path.exists(file_path + str(num)):
    os.mkdir(file_path + str(num))

batch_num = 20 # 20
numfiles = len([name for name in os.listdir(file_path + str(num) +"\\") if os.path.isfile(file_path + str(num) + "\\" + name)])

if FIND_NUM_TARGET_FLAG:
    # loop including brute force method
    # what are the test case limits of brute force?
    # based on num of combinations.
    # Cap num interceptors to be 2x that of targets
    
    BF_FLAG = 1
    num_interceptor_platforms_range = [10,10]
    V_lims = [1,10]
    num_tests = 100/batch_num
    
    GREEDY_FLAG = 1
    WTA_FLAG = 1
    while numfiles < batch_num:
        for num_targets in range(2,10):
            if num_targets == 1:
                pass
            else:
                num_targets_range = [num_targets,num_targets]
            print("Running tests for num_targets_range = {}".format(num_targets_range))
            W_lims = [1,num_targets]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
             
        print("Writing files")
        with open(file_path + str(num) + "\\stress_test_vary_w_{}.csv".format(str(numfiles+1)),'w',newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for row in datalog:
                writer.writerow(row)
        print("Files written")
        
        # updating data for the next loop
        datalog = []
        numfiles = len([name for name in os.listdir(file_path + str(num) +"\\") if os.path.isfile(file_path + str(num) + "\\" + name)])
        
if V_TEST_FLAG:
    # to determine appropriate range of V for WTA to work well, using 5v5 case
    BF_FLAG = 1
    num_interceptor_platforms_range = [5,5]
    num_targets_range = [10,10]
    GREEDY_FLAG = 1
    WTA_FLAG = 1
    V_upper_arr = [10,20,30,40,50]
    W_lims = [1,10]
    num_tests = 100/batch_num
    counts = []
    while numfiles < batch_num:
        for V_upper in V_upper_arr:
            print("Running tests for V_upper = {}".format(V_upper))
            V_lims = [1,V_upper]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG, GREEDY_FLAG, BF_FLAG, timeout)
            # count = 0
            # for entry in datalog:
                # if entry[3] == "WTA Solver Error":
                    # count+=1
            # counts.append(count)
        # for i in range(len(counts)):
            # print("% failed cases for V_upper {}: {}%".format(V_upper_arr[i],counts[i]/num_tests*100))
            
        print("Writing files")
        with open(file_path + str(num) + "\\stress_test_vary_v_{}.csv".format(str(numfiles+1)),'w',newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for row in datalog:
                writer.writerow(row)
        print("Files written")
        
        # updating data for the next loop
        datalog = []
        numfiles = len([name for name in os.listdir(file_path + str(num) +"\\") if os.path.isfile(file_path + str(num) + "\\" + name)])
        
if BF_TEST_FLAG:
    BF_FLAG = 1
    num_interceptor_platforms_range = [5,5]
    W_lims = [1,5]
    V_lims = [1,10]
    num_tests = 200/batch_num
    WTA_FLAG = 1
    GREEDY_FLAG = 1
    while numfiles < batch_num:
        for x in range(2,7):
            # x targets for x from 2 to 6
            num_targets_range = [x,x]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            
        print("Writing files")
        with open(file_path + str(num) + "\\assignments_BF_{}.csv".format(str(numfiles+1)),'w',newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for row in datalog:
                writer.writerow(row)
        print("Files written")
    
        # updating data for the next loop
        datalog = []
        numfiles = len([name for name in os.listdir(file_path + str(num) +"\\") if os.path.isfile(file_path + str(num) + "\\" + name)])
    
if MAIN_TEST_FLAG:
    BF_FLAG = 0
    # Test Cases to consider
    
    # 1 interceptor vs many targets (5,000)
    num_interceptor_platforms_range = [1,1]
    GREEDY_FLAG = 1
    WTA_FLAG = 1
    V_lims = [1,10]
    num_tests = 200/batch_num
    while numfiles < batch_num:
        # loop will keep writing more files into an existing folder until it reaches the batch_num

        # 2-10 targets
        print("Stage 1-1")
        num_targets_range = [2,10]
        W_lims = [1,10]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG, BF_FLAG, timeout)
        # 11-20 targets
        print("Stage 1-2")
        num_targets_range = [11,20]
        W_lims = [1,20]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG, BF_FLAG, timeout)
        # 21-30 targets
        print("Stage 1-3")
        num_targets_range = [21,30]
        W_lims = [1,30]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG, BF_FLAG, timeout)
        # 31-40 targets
        print("Stage 1-4")
        num_targets_range = [31,40]
        W_lims = [1,40]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
        # 41-50 targets
        print("Stage 1-5")
        GREEDY_FLAG = 1
        num_targets_range = [41,50]
        W_lims = [1,50]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
        # 51-100 targets
        print("Stage 1-6")
        num_targets_range = [51,100]
        W_lims = [1,100]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
        # 101-200 targets
        print("Stage 1-7")
        num_targets_range = [101,200]
        W_lims = [1,200]
        run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
        
        # many interceptors vs many targets (5,000)
        
        # interceptors platforms (less options as from the perspective of a defender, too many platforms make it hard to maintain and operate)
        # 5 (2500)
        # 10 (2500)
        num_interceptor_platforms_choices = [5,10]
        
        V_lims = [1,10]
        num_tests = 200/batch_num
        i=1
        for num_interceptor_platforms in num_interceptor_platforms_choices:
            WTA_FLAG = 1
            GREEDY_FLAG = 1
            i+=1
            # assume no. interceptors >= targets
            num_interceptor_platforms_range = [num_interceptor_platforms,num_interceptor_platforms]
            # targets
            # 2-10 (500x2)
            print("Stage {}-1".format(i))
            num_targets_range = [2,10]
            W_lims = [1,10]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            # 11-20
            print("Stage {}-2".format(i))
            num_targets_range = [11,20]
            W_lims = [1,20]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            # 21-30
            print("Stage {}-3".format(i))
            num_targets_range = [21,30]
            W_lims = [1,30]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            # 31-40
            print("Stage {}-4".format(i))
            num_targets_range = [31,40]
            W_lims = [1,40]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            # 41-50
            print("Stage {}-5".format(i))
            num_targets_range = [41,50]
            W_lims = [1,50]
            GREEDY_FLAG = 1
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            # 51-100
            print("Stage {}-6".format(i))
            num_targets_range = [51,100]
            W_lims = [1,100]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
            # 100-200
            print("Stage {}-7".format(i))
            num_targets_range = [101,200]
            W_lims = [1,200]
            run_test(num_interceptor_platforms_range, num_targets_range, W_lims, V_lims, num_tests,datalog,WTA_FLAG,GREEDY_FLAG,BF_FLAG, timeout)
        
        print("Writing files")
        with open(file_path + str(num) + "\\assignments_{}.csv".format(str(numfiles+1)),'w',newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for row in datalog:
                writer.writerow(row)
        print("Files written")
                
        # updating data for the next loop
        datalog = []
        numfiles = len([name for name in os.listdir(file_path + str(num) +"\\") if os.path.isfile(file_path + str(num) + "\\" + name)])