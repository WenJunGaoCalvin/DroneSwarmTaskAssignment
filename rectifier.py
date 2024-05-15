# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:44:07 2024

@author: Asus
"""
import csv

file_path = "C:\\Users\Asus\\OneDrive - National University of Singapore\\FYP\\Task Assignment\\results\\"
folder = "find_v"
filename = "\\full.csv"
write_file="\\full_updated.csv"

datalog = []

with open (file_path + folder + filename, 'r') as file:
    reader = csv.reader(file)
    topics = next(reader)
    for row in reader:
        W = [int(float(i)) for i in row[5][1:-1].split(', ')]
        deployed = [j for j in row[3][1:-1].split(', ')]
        for k in range(len(deployed)):
            try: 
                if int(float(deployed[k])) > sum(W):
                    row[13+k] = 1
                else:
                    row[13+k] = 0
            except:
                row[13+k] = 0
        datalog.append(row)

print("Writing files")
with open (file_path + folder + write_file, 'w',newline='') as file:
    writer = csv.writer(file,delimiter=",")
    writer.writerow(topics)
    for row in datalog:
        writer.writerow(row)
print("Files Written")