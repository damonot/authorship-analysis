# Calculate Degree Correlation Assortativity of given repository arranged by author and by file of origin
import os
def runner(repoAddress):
    repo = repoAddress.rsplit('/', 1)[-1] # last part of gitURL

    cwd = os.getcwd()
    authDCA = cwd+"\\text_data\otero-"+repo+"-authDCA.txt"
    fileDCA = cwd+"\\text_data\otero-"+repo+"-fileDCA.txt"

    dcas = [authDCA, fileDCA]


    for dca in dcas:
      dcaDict = create_dict(dca)
      dcaVal = calc_dca(dcaDict)

def count_edges(dcaDict):
  edges = 0
  for key in dcaDict.keys():
    edges += int(dcaDict[key])

  return edges

def calc_dca(dcaDict):
  allEdges = count_edges(dcaDict)

def create_dict(dca):
  degfreqPairs = {}
  with open (dca, encoding='UTF-8') as f:
    next(f)
    for line in f:
      (key, val) = line.split('\t')
      degfreqPairs[key] = val

  return degfreqPairs

      
