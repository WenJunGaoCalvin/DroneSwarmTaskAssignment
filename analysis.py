# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 10:37:15 2024

@author: Asus
"""
import csv
import os
import math

# Optimality component
file_path = "C:\\Users\Asus\\OneDrive - National University of Singapore\\FYP\\Task Assignment\\results\\"
folder = "5\\"
filename = "full.csv"

BF_FLAG = 0
MAIN_FLAG = 1
### SHARED AMONGST TESTS
wta_scores = []
greedy_scores = []

wta_error_count = 0

wta_times = []
greedy_times = []

if BF_FLAG:
    ### SPECIFIC TO BF TESTS
    bf_scores = []
    bf_times = []
    
    wta_opts = []
    greedy_opts = []
    
    greedy_profit_per_asset_deployed = []
    wta_profit_per_asset_deployed=[]
    bf_profit_per_asset_deployed=[]
    
    wta_opt_above_one = 0
    wta_opt_equal_one = 0
    wta_opt_below_one = 0
    
    greedy_opt_above_one = 0
    greedy_opt_equal_one = 0
    greedy_opt_below_one = 0
    
    wta_solver_error_count = 0
    

    
    with open (file_path + folder + filename, 'r') as file:
        csvreader = csv.reader(file)
        topics = next(csvreader)
        for row in csvreader:
            
            bf_score = float(row[12])
            bf_scores.append(bf_score)
            V_sum = sum([float(i) for i in row[4][1:-1].split(', ')])
            
            try:
                wta_score = float(row[10])
                wta_scores.append(wta_score)
                wta_opt = wta_score/bf_score
                wta_opts.append(wta_opt)
                if wta_opt > 1:
                    wta_opt_above_one +=1
                elif wta_opt == 1:
                    wta_opt_equal_one += 1
                else:
                    wta_opt_below_one += 1
                    
                wta_deployed = float(row[3][1:-1].split(', ')[0])
                if wta_deployed != 0:
                    wta_efficiency_score = (V_sum - wta_score)/wta_deployed
                else:
                    wta_efficiency_score = "Undefined"
                wta_profit_per_asset_deployed.append(wta_efficiency_score)
            except:
                wta_solver_error_count +=1
                wta_profit_per_asset_deployed.append(-1)
            
            greedy_score = float(row[11])
            greedy_scores.append(greedy_score)
            greedy_opt = greedy_score/bf_score
            greedy_opts.append(greedy_opt)
            if greedy_opt >1:
                greedy_opt_above_one += 1
            elif greedy_opt == 1:
                greedy_opt_equal_one += 1
            else:
                greedy_opt_below_one += 1
                        
            wta_times.append(float(row[-3]))
            greedy_times.append(float(row[-2]))
            bf_times.append(float(row[-1]))
            
            
            greedy_deployed = float(row[3][1:-1].split(', ')[1])
            if greedy_deployed != 0:
                greedy_efficiency_score = (V_sum - greedy_score)/greedy_deployed
            else:
                greedy_efficiency_score = "Undefined"
            greedy_profit_per_asset_deployed.append(greedy_efficiency_score)
            
            bf_deployed = float(row[3][1:-1].split(', ')[2])
            if bf_deployed != 0:
                bf_efficiency_score = (V_sum - bf_score)/bf_deployed
            else:
                bf_efficiency_score = "Undefined"
            bf_profit_per_asset_deployed.append(bf_efficiency_score)
    
    # processing
    numtests = len(wta_times)
    
    wta_avg_opt = sum(wta_opts)/len(wta_opts) # excludes cases with solver errors
    greedy_avg_opt = sum(greedy_opts)/len(greedy_opts)
    
    tmp = [i for i in wta_profit_per_asset_deployed if (type(i)==float and i!=-1)]
    wta_avg_eff = sum(tmp)/len(tmp)
    
    tmp = [i for i in greedy_profit_per_asset_deployed if type(i)==float]
    greedy_avg_eff = sum(tmp)/len(tmp)
    
    tmp = [i for i in bf_profit_per_asset_deployed if type(i)==float]
    bf_avg_eff = sum(tmp)/len(tmp)
    
    # wta_percent_error = wta_solver_error_count/numtests*100
    
    wta_percent_above_one = wta_opt_above_one/len(wta_opts)*100
    greedy_percent_above_one = greedy_opt_above_one/len(greedy_opts)*100
    
    print("Number of entries: {}".format(numtests))
    print("Average Optimality Ratio for IPOPT: {}".format(wta_avg_opt))
    print("Average Optimality Ratio for Greedy: {}".format(greedy_avg_opt))
    # print("Solver Error % for WTA algorithm: {}%".format(wta_percent_error))
    print("Average Efficiency Ratio for IPOPT: {}".format(wta_avg_eff))
    print("Average Efficiency Ratio for Greedy: {}".format(greedy_avg_eff))
    print("Average Efficiency Ratio for BF: {}".format(bf_avg_eff))
    
    print("% Optimality above 1 for IPOPT: {}%".format(wta_percent_above_one))
    print("% Optimality above 1 for Greedy: {}%".format(greedy_percent_above_one))
    
    print("% Optimality equal 1 for IPOPT: {}%".format(wta_opt_equal_one/len(wta_opts)*100))
    print("% Optimality equal 1 for Greedy: {}%".format(greedy_opt_equal_one/len(greedy_opts)*100))
    
    print("% Optimality below 1 for IPOPT: {}%".format(wta_opt_below_one/len(wta_opts)*100))
    print("% Optimality below 1 for Greedy: {}%".format(greedy_opt_below_one/len(greedy_opts)*100))
    
    
    print("Average Computation Time for IPOPT: {}s".format(sum(wta_times)/numtests))
    print("Average Computation Time for Greedy: {}s".format(sum(greedy_times)/numtests))
    print("Average Computation Time for BF: {}s".format(sum(bf_times)/numtests))
    
    

if MAIN_FLAG:
    def get_averages(data,write_file):
        # compute averages, for wta, if -1, do not compute into average
        averages = [[] for i in range(len(data))]
        for i in range(len(data)):
            phase = data[i]
            
            phase_processed = [row for row in phase if row[7] != "Undefined"]
            error_count = 0
            total = 0
            #for each result
            for j in range(len(phase_processed[0])):
                result = 0
                count = 0
                total = 0
                # for each entry
                for k in range(len(phase_processed)):
                    if phase_processed[k][j] != -1:
                        result += phase_processed[k][j]
                        count += 1
                    else:
                        error_count +=1
                    total += 1
                average = result/count
                averages[i].append(average)
            averages[i].append(error_count/total*100)
        
            wta_timeout_count = 0
            greedy_timeout_count = 0
            timeout = 60
            
            print("Total:",total)
            for row in phase_processed:
                wta_time = row[2]
                greedy_time = row[3]
                # print(wta_times)
                if wta_time >= timeout:
                    wta_timeout_count += 1
                if greedy_time >= timeout:
                    greedy_timeout_count += 1
            print("IPOPT Timeout Rate: {}%".format(wta_timeout_count/total*100))
            print("Greedy Timeout Rate: {}%".format(greedy_timeout_count/total*100))
        topics = ['wta_scores','greedy_scores','wta_times','greedy_times',
                'wta_assets_deployed','greedy_assets_deployed','wta_profit_per_asset_deployed',
                'greedy_profit_per_asset_deployed','is_impossible','wta_percent_error']
        with open (file_path + folder + write_file, 'w',newline='') as file:
            writer = csv.writer(file,delimiter=",")
            writer.writerow(topics)
            for row in averages:
                writer.writerow(row)
    wta_assets_deployed = []
    greedy_assets_deployed = []
    wta_profit_per_asset_deployed = []
    greedy_profit_per_asset_deployed = []
    entry_id = []
    is_impossible = []
    with open (file_path + folder + filename, 'r') as file:
        csvreader = csv.reader(file)
        topics = next(csvreader)
        for row in csvreader:
            # print(row)
            entry_id.append(int(row[0]))
            
            V_sum = sum([float(i) for i in row[4][1:-1].split(', ')])
            
            greedy_score = float(row[10])
            greedy_scores.append(greedy_score)
                  
            wta_times.append(float(row[11]))
            greedy_times.append(float(row[12]))
            greedy_deployed = float(row[3][1:-1].split(', ')[1])
            greedy_assets_deployed.append(greedy_deployed)
            if greedy_score != 0:
                # greedy_efficiency_score = math.log(1/(greedy_score*greedy_deployed))
                # greedy_efficiency_score = -1*math.log(greedy_score*greedy_deployed)
                greedy_efficiency_score = (V_sum - greedy_score)/greedy_deployed
            else:
                greedy_efficiency_score = "Undefined"
            greedy_profit_per_asset_deployed.append(greedy_efficiency_score)
            
            try:
                wta_score = float(row[9])
                wta_scores.append(wta_score)
                wta_deployed = float(row[3][1:-1].split(', ')[0])
                wta_assets_deployed.append(wta_deployed)
                if wta_score != 0:
                    # wta_efficiency_score = math.log(1/(wta_score*wta_deployed))
                    # wta_efficiency_score = -1*math.log(wta_score*wta_deployed)
                    wta_efficiency_score = (V_sum - wta_score)/wta_deployed
                else:
                    wta_efficiency_score = "Undefined"
                wta_profit_per_asset_deployed.append(wta_efficiency_score)
                is_impossible.append(wta_deployed > greedy_deployed)
            except:
                wta_error_count +=1
                wta_scores.append(-1)
                wta_assets_deployed.append(-1)
                wta_profit_per_asset_deployed.append(-1)
                is_impossible.append(-1)
    
    # segment into categories, by platforms, then targets
    phase1 = [] # 1 platform
    phase2 = [] # 5 platforms
    phase3 = [] # 10 platforms
    numtargets1 = [] # [2,10]
    numtargets2 = [] # [11,20]
    numtargets3 = [] # [21,30]
    numtargets4 = [] # [31,40]
    numtargets5 = [] # [41,50]
    numtargets6 = [] # [51,100]
    numtargets7 = [] # [101,200]
    
    # sort by platforms
    for i in range(len(entry_id)):
        if entry_id[i]//1000 == 1:
            phase1.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if entry_id[i]//1000 == 5:
            phase2.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if entry_id[i]//1000 == 10:
            phase3.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
    phases = [phase1,phase2,phase3]
    write_file = "averages_by_platform.csv"
    get_averages(phases,write_file)
    
    for i in range(len(entry_id)):
        if 2 <= entry_id[i]%1000 <= 10:
            numtargets1.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if 11 <= entry_id[i]%1000 <= 20:
            numtargets2.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if 21 <= entry_id[i]%1000 <= 30:
            numtargets3.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if 31 <= entry_id[i]%1000 <= 40:
            numtargets4.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if 41 <= entry_id[i]%1000 <= 50:
            numtargets5.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if 51 <= entry_id[i]%1000 <= 100:
            numtargets6.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
        if 101 <= entry_id[i]%1000 <= 200:
            numtargets7.append([wta_scores[i],greedy_scores[i],wta_times[i],greedy_times[i],
                           wta_assets_deployed[i],greedy_assets_deployed[i],wta_profit_per_asset_deployed[i],
                           greedy_profit_per_asset_deployed[i],is_impossible[i]])
            
    datas = [numtargets1,numtargets2,numtargets3,numtargets4,numtargets5,numtargets6,numtargets7]
    write_file = "averages_by_targets.csv"
    get_averages(datas,write_file)
            
    
    