# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 22:10:56 2024

@author: Asus
"""
import os
import csv

file_path = "C:\\Users\Asus\\OneDrive - National University of Singapore\\FYP\\Task Assignment\\results\\"
folder = "with_bf\\"
batch_num = 20
files = [name for name in os.listdir(file_path + folder) if os.path.isfile(file_path + folder + name)]

BF_FLAG = 1
MAIN_FLAG = 0

dataset = []
for file in files:
    with open(file_path + folder + file, newline='') as f:
        reader = csv.reader(f)
        # for every row, first element is num_inter_platforms, second element is num_targets
        # arrange in order of platforms first, then targets
        data = list(reader)
        dataset += data
        
# sort rows by rank
# sorted_dataset = sorted(dataset, key=lambda x: x[0])

# sort rows by max Vi value
f = lambda x: max([int(float(i)) for i in x[4][1:-1].split(', ')])
sorted_dataset = sorted(dataset, key=f)

if MAIN_FLAG:
    topics = ['rank','num_int','num_targets','interceptors_deployed','V',
              'W','p','WTA_X', 'Greedy_X','WTA_score', 'Greedy_score', 
              'ipopt_is_unfeasible','G_is_unfeasible','WTA_time', 'Greedy_time']
if BF_FLAG:
    topics = ['rank','num_int','num_targets','interceptors_deployed','V',
              'W','p','WTA_X', 'Greedy_X', 'BF_X','WTA_score', 'Greedy_score', 
              'BF_score','ipopt_is_unfeasible','G_is_unfeasible','BF_is_unfeasible',
              'WTA_time', 'Greedy_time', 'BF_time']
with open(file_path + folder + 'full.csv', mode='w', newline='') as data_file:
    data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data_writer.writerow(topics)
    for row in sorted_dataset:
        data_writer.writerow(row)

print("Batches combined into full.csv")