import bicon

def test(verbose, overwrite, repo):
    print("hello")


def gather_data(txt, repo):
    print("biclustering")
    data = get_numerical_data(txt, repo)


    #TODO move this section to makegraphdata.py
    response = input("Generate new Bicluster Data? [y]/n")
    if(response == 'y'):
        network = get_network(data)
        ffiaf2excel(data, repo, "BiCluster")
        network2excel(network, repo, "BiCluster")
    bicon_analysis(repo)


def bicon_analysis(repo):

    folder = "xl_data\\"
    path_expr = folder + "otero-"+repo+"-biconExprs.csv"
    path_net = folder + "otero-"+repo+"-biconNetwork.tsv"

    GE,G,labels, _= data_preprocessing(path_expr, path_net)
    L_g_min = 10
    L_g_max = 15
    model = BiCoN(GE,G,L_g_min,L_g_max)
    solution,scores= model.run_search()

    results = results_analysis(solution, labels)
    results.convergence_plot(scores)

    resultLoc = folder + "otero-"+repo+"-biconResults.csv"
    results.save(output = resultLoc)

    netOut = folder + "otero-"+repo+"-biconNetwork.png"
    results.show_networks(GE, G, output = netOut)
    
    clusterOut = folder + "otero-"+repo+"-biconClustermap.png"
    results.show_clustermap(GE, G, output = clusterOut)


def get_numerical_data(txt, repo):
    flaws = []
    authors = []
    flawLines = []
    with open(txt, encoding='utf-8') as t:
        for line in t:
            fields = line.split('\t') # 0auth | 1file | 2flawtype | 3line | 4rule |
            flawLines.append(fields) # copy necessary lines into list
            flaw = fields[4]
            auth = fields[0]
            if(flaw not in flaws): # flaw not encountered yet
                flaws.append(flaw)
            if(auth not in authors): # author not encountered yet
                authors.append(auth)
    
    nAuth = len(authors) # number of authors
    
    #FF calculation
    listDict = [] # list of freqDict
    for auth in authors:
        freqDict = {} # of times each flaw is connected to auth
        for line in flawLines:
            if(line[0] == auth):
                flaw = line[4]
                if(flaw not in freqDict):
                    freqDict[flaw] = 1
                else:
                    freqDict[flaw] +=1
        
        listDict.append([auth, freqDict]) # author & their flaw freq dist
    
    '''structure is...
    list: tups
        tup: author, dict
            dict: flaw, freq '''

    return listDict


def get_network(data):
    allperms = []
    for tup in data:
        flaws = []
        for flaw in tup[1]:
            flaws.append(flaw.rstrip())
        flawperms = permutations(flaws, 2)
        for perm in list(flawperms):
            if(perm not in allperms):
                allperms.append(perm)
    
    print(allperms)
    return allperms


def ffiaf2excel(ffiaf, repo, type):
    
    #print(bfiaf)
    folder = "xl_data\\"
    if(type == "Bug"):
        xlname = folder + "otero-bfiaf.xlsx"
    if(type == "Vulnerability"):
        xlname = folder + "otero-vfiaf.xlsx"
    if(type == "AUTHOR"):
        xlname = folder + "otero-"+repo+"-authorProxmeasure.xlsx"
        type = "Bug"
    if(type == "FILE"):
        xlname = folder + "otero-"+repo+"-fileProxmeasure.xlsx"
        type = "Bug"
    if(type == "BiCluster"):
        xlname = folder + "otero-"+repo+"-biconData.xlsx"
        type = "Flaw"
    try:
        book = load_workbook(xlname)
    except:
        book = openpyxl.Workbook()
        default = book.get_sheet_by_name('Sheet')
        book.remove_sheet(default)

    sheet = book.create_sheet(repo)

    # generate column headers
    cl = sheet.cell(row=1, column=1)
    cl.value = type+"_Rule"
    col = 2; row = 1
    for tups in ffiaf:
        cl = sheet.cell(row=row, column=col)
        cl.value = tups[0]
        col+=1

    # generate row headers i.e. rule types
    rules = []
    for tups in ffiaf:
        for rule in tups[1]:
            cleanRule = (rule.replace('\n', ''))
            if(cleanRule not in rules):
                rules.append(cleanRule)
    col = 1; row = 2;
    for rule in rules:
        cl = sheet.cell(row=row, column=col)
        cl.value = rule
        #sheet.write(row,col, rule)
        row+=1

    '''
    structure is...
    list: tups
        tup: author, dict
            dict: flaw, freq 
    '''


    # populate table 
    col = 2
    for tups in ffiaf:
        dict = tups[1]
        for rule in dict:
            row = 2
            cleanRule = (rule.replace('\n', ''))
            cl = sheet.cell(row=row, column=1)
            rowRule = cl.value
            while(rowRule != cleanRule):
                row+=1
                cl = sheet.cell(row=row, column=1)
                rowRule = cl.value
            cl = sheet.cell(row=row, column=col)
            cl.value = dict[rule]
            #print(rule, dict[rule])
        col+=1


    book.save(xlname)


def network2excel(network, repo, type):
    folder = "xl_data\\"

    xlname = folder + "otero-"+repo+"-biconExprs.xlsx"
    try:
        book = load_workbook(xlname)
    except:
        book = openpyxl.Workbook()
        default = book.get_sheet_by_name('Sheet')
        book.remove_sheet(default)

    sheet = book.create_sheet(repo)


    row = 1
    for conn in network:
        col = 1
        cl = sheet.cell(row=row, column=col)
        cl.value = conn[0]
        col+=1
        cl = sheet.cell(row=row, column=col)
        cl.value = conn[1]
        row+=1

    book.save(xlname)
