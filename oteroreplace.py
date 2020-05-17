# replace the descriptions of the flaw with the SonarQube rule that the flaw violated
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

  for i in range(len(txts)):
     tempRules = rule_grabber(csvs[i])
     tempTXT = desc_swapper(txts[i], tempRules)
     replace_txt(tempTXT, txts[i])

def replace_txt(tempTXT, txtName):
  with open(txtName, "w", encoding='utf-8') as file:
    ruleIndex = 0
    for line in tempTXT:
      file.write(line)

def desc_swapper(txtLoc, tempRules):
  newLines = []
  with open(txtLoc, "r+", encoding='utf-8') as file:
    ruleIndex = 0
    for line in file:
        fields = line.split('\t')
        oldLine = fields[:4]
        rule = tempRules[ruleIndex] + "\n"
        
        newLine = ""
        for item in oldLine:
          newLine+=item+"\t"
        newLine+=rule
        newLines.append(newLine)
        print(newLine)
        ruleIndex+=1
  return newLines

def rule_grabber(csvLoc):
  rules = []
  with open(csvLoc) as fd:
        for row in islice(csv.reader(fd), 1, None): # skips header
          rules.append(row[4])
  return rules