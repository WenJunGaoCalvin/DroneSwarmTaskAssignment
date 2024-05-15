# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 19:03:43 2024

@author: Asus
"""
import csv
import pandas as pd

file_path = "C:\\Users\Asus\\OneDrive - National University of Singapore\\FYP\\Task Assignment\\results\\"
folder = "find_v"
filename = "\\full_updated.csv"
write_file = "\\stress_test_vary_v_analysis.csv"
timeout = 60
num_tests = 100

with open (file_path + folder + filename, 'r') as file:
        
    ipopt_is_unfeasible_counts = []
    g_is_unfeasible_counts = []
    bf_is_unfeasible_counts = []
    
    ipopt_error_counts = []
    g_error_counts = []
    bf_error_counts = []
    
    ipopt_timout_counts = []
    g_timout_counts = []
    bf_timout_counts = []
    
    total_count = 0
    
    ipopt_is_unfeasible_count = 0
    g_is_unfeasible_count = 0
    bf_is_unfeasible_count = 0
    
    ipopt_error_count = 0
    g_error_count = 0
    bf_error_count = 0
    
    ipopt_timout_count = 0
    g_timout_count = 0
    bf_timout_count = 0
    
    csvreader = csv.reader(file)
    topics = next(csvreader)
    for data in csvreader:
    
        total_count += 1
    
        ipopt_is_unfeasible_count += float(data[13])
        g_is_unfeasible_count += float(data[14])
        bf_is_unfeasible_count += float(data[15])
        
        if float(data[-3]) >= timeout:
            ipopt_timout_count += 1
        if float(data[-2]) >= timeout:
            g_timout_count += 1
        if float(data[-1]) >= timeout:
            bf_timout_count += 1
        
        try:
            wta_deployed = float(data[3][1:-1].split(', ')[0])
        except:
            ipopt_error_count += 1
            
        if total_count == num_tests:
            ipopt_is_unfeasible_counts.append(ipopt_is_unfeasible_count)
            g_is_unfeasible_counts.append(g_is_unfeasible_count)
            bf_is_unfeasible_counts.append(bf_is_unfeasible_count)
            
            ipopt_error_counts.append(ipopt_error_count)
            g_error_counts.append(g_error_count)
            bf_error_counts.append(bf_error_count)
            
            ipopt_timout_counts.append(ipopt_timout_count)
            g_timout_counts.append(g_timout_count)
            bf_timout_counts.append(bf_timout_count)
            
            total_count = 0
            
            ipopt_is_unfeasible_count = 0
            g_is_unfeasible_count = 0
            bf_is_unfeasible_count = 0
            
            ipopt_error_count = 0
            g_error_count = 0
            bf_error_count = 0
            
            ipopt_timout_count = 0
            g_timout_count = 0
            bf_timout_count = 0
        
topics = ['IPOPT % unfeasible','G % unfeasible','BF % unfeasible',
         'IPOPT % error','G % error','BF % error',
         'IPOPT % timeout','G % timeout','BF % timeout']
    
print("Writing files")
with open (file_path + folder + write_file, 'w',newline='') as file:
    writer = csv.writer(file,delimiter=",")
    writer.writerow(topics)
    for i in range(len(ipopt_is_unfeasible_counts)):
        data = [ipopt_is_unfeasible_counts[i]/num_tests*100,
                g_is_unfeasible_counts[i]/num_tests*100,
                bf_is_unfeasible_counts[i]/num_tests*100,
                ipopt_error_counts[i]/num_tests*100,
                g_error_counts[i]/num_tests*100,
                bf_error_counts[i]/num_tests*100,
                ipopt_timout_counts[i]/num_tests*100,
                g_timout_counts[i]/num_tests*100,
                bf_timout_counts[i]/num_tests*100]
        writer.writerow(data)
print("Files written")
"""
    for i in range(len(average_times)):
        print("Average computation time for {} targets: {}s".format(i+2,average_times[i]))
        print("% timeout cases for {} targets: {}%".format(i+2,timout_counts[i]/num_tests*100))
        print("% solver error cases for {} targets: {}%".format(i+2,error_counts[i]/num_tests*100))
        print("% solver unfeasible cases for {} targets: {}%".format(i+2,is_unfeasible_counts[i]/num_tests*100))
"""