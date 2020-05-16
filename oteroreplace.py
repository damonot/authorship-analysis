import csv
from itertools import islice # csv iteration
import os
def runner():
  csvs = [
  "raw_data\otero-drupal-bug.csv",
  "raw_data\otero-drupal-vuln.csv",
  "raw_data\otero-moodle-bug.csv",
  "raw_data\otero-moodle-vuln.csv",
  "raw_data\otero-phpmyadmin-bug.csv",
  "raw_data\otero-phpmyadmin-vuln.csv",
  ]

  txts = [
    "text_data\otero-drupal-auth2bug.txt",
    "text_data\otero-drupal-auth2vuln.txt",
    "text_data\otero-moodle-auth2bug.txt",
    "text_data\otero-moodle-auth2vuln.txt",
    "text_data\otero-phpmyadmin-auth2bug.txt",
    "text_data\otero-phpmyadmin-auth2vuln.txt",    
  ]

  for i in range(0,9):
     tempRules = rule_grabber(csvs[i])
    

  for txt in txts:
    tempDesc = desc_grabber(txt)

def desc_grabber(txtLoc):
  descs = []
  with open(txtLoc, "r+", encoding='utf-8') as file:
    for line in file:
        fields = line.split('\t')
        #print(fields[4])
        #descs.append(fields[3])


def rule_grabber(csvLoc):
  rules = []
  with open(csvLoc) as fd:
        for row in islice(csv.reader(fd), 1, None): # skips header
          rules.append(row[4])
  return rules