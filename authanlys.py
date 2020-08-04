'''Damon Otero. https://github.com/damonot''' 
import re
import os
import shutil
import argparse
import scripts.oteromakegraphdata as mkgrf
import scripts.oteroanalyzegraphs as anlyzgrf
import scripts.check as check
import scripts.setupbicluster as setupbicluster

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbose", 
                        help="increase output verbosity.",
                        action="store_true")
    
    parser.add_argument("-r", "--runall", 
                        help="run all generative, and analytical functions of program for all repositories.",
                        action="store_true")

    parser.add_argument("-i", "--ignore", 
                        help="exempt specific repositories, generative, or analytical functions of program from --runall. e.g. to exempt biclustering, use '--ignore bicluster'",
                        nargs="+", type=str)

    parser.add_argument("--deleteall", 
                        help="delete all .txt and .xlsx files created by authanalys.py",
                        action="store_true")

    parser.add_argument("-o", "--overwrite", 
                        help="overwrite pre-existing .txt and .xlsx files created in a previous previauthanlys.py launch",
                        action="store_true")

    parser.add_argument("-cr", "--clonerepo", 
                        help="download repository to local machine via Git")

    parser.add_argument("-co", "--combine", 
                        help="run analyses on combination of the repositories as opposed to independently",
                        action="store_true")

    parser.add_argument("-b", "--bicluster", 
                        help="'BiCon' biclustering analysis of authors and code flaws.",
                        action="store_true")

    parser.add_argument("-d", "--dca", 
                        help="degree correlation assortativity (DCA) analysis of coworkers and code flaws.",
                        action="store_true")

    parser.add_argument("-ce", "--centrality", 
                        help="Generate centrality scores for Authors & Files",
                        action="store_true")

    parser.add_argument("-ff", "--ffiaf", 
                        help="Flaw-Frequency * Inverse Author Frequency (FFIAF) analysis of authors and code flaws.",
                        action="store_true")

    parser.add_argument("-av", "--authvuln", 
                        help="generate .txt of authors and vulnerabillities from raw csv.",
                        action="store_true")

    parser.add_argument("-ab", "--authbug", 
                        help="generate .txt of authors and bugs from raw csv.",
                        action="store_true")       
    
    parser.add_argument("-af", "--authflaw", 
                    help="combine output of --authbug and --authvuln.",
                    action="store_true") 

    parser.add_argument("-ai", "--authinfluence", 
                    help="Calculate influence of each author, output to .txt.",
                    action="store_true") 

    parser.add_argument("-fl", "--flaws", 
                        help="generate .txt of flaws linked by author or by file.",
                        action="store_true")      

    parser.add_argument("-cw", "--coworkers", 
                        help="generate .txt of coworkers; authors of flaws from the same file.",
                        action="store_true")

    parser.add_argument("--lynks", 
                    help="generate Lynksoft-formatted XLSX of existing .txt files.",
                    action="store_true")

    args = parser.parse_args()

    if(args.ignore):
        validate_ignored(args.ignore, args)

    if args.verbose:
        print("Verbose Mode On")
    if args.overwrite:
        print("Overwrite Mode On")        

    repos = grab_repos()
    for repo in repos:
        go(args, repo)
        # make sure trueall() and ignore() are updated with all params

    if args.combine:
        #handle_prev_combined(args.verbose, args.overwrite)
        combine_mkgrf_data(args, repos) 
        go(args, "combinedrepos")



    print("\nDone.")


def combine_mkgrf_data(args, repos):
    if args.authflaw:
        authbug = True
        authvuln = True

    # combine authbug
    if args.authbug:
        combine_txt(args.verbose, args.overwrite, "bug", repos)
    
    # combine authvuln
    if args.authvuln:
        combine_txt(args.verbose, args.overwrite, "vuln", repos)

    # combine authflaw
    if args.authflaw:
        combine_txt(args.verbose, args.overwrite, "flaw", repos)


def combine_txt(verbose, overwrite, type, repos):
    if repos is None:
        repos = grab_repos()
    
    print("combining data from: " + ', '.join(repos))

    fileList = []
    for repo in repos:
        fileLoc = os.getcwd() + '\output\{}\{}-auth{}.txt'.format(repo, repo, type) 
        fileList.append(fileLoc)

        if(not check.fyle(verbose, repo, fileLoc)):
            if verbose:
                print("\t{} DNE".format(fileLoc))
            func = getattr(mkgrf, 'auth_'+type)
            func(verbose, overwrite, repo)

    out = os.getcwd() + '\output\combinedrepos\combinedrepos-auth{}.txt'.format(type)
    check.folder(verbose, "combinedrepos")

    mkgrf.merge_files(verbose, overwrite, fileList, out)


def go(args, repo):
    if args.verbose:
        print("\n====={} active=====".format(repo))
        
    if args.runall:
        if args.verbose:
            print("\nRunning all functions for {}; ignoring {}".format(repo, args.ignore))
        args = trueall(args)
        args = ignore(args)

    if repo != 'combinedrepos':
        if args.authvuln:
            mkgrf.auth_vuln(args.verbose, args.overwrite, repo)

        if args.authbug:
            mkgrf.auth_bug(args.verbose, args.overwrite, repo)
        
        if args.authflaw:
            mkgrf.auth_flaw(args.verbose, args.overwrite, repo)   


    '''
    if args.coworkers:
        mkgrf.coworkers(args.verbose, args.overwrite, repo)

    if args.flaws:
        mkgrf.flaws(args.verbose, args.overwrite, repo)

    if args.lynks:
        mkgrf.lynks(args.verbose, args.overwrite, repo)
    '''

    if args.authinfluence:
        anlyzgrf.auth_influence(args.verbose, args.overwrite, repo)

    if args.bicluster:
        setupbicluster.go(args.verbose, args.overwrite, repo)

    if args.centrality:
        anlyzgrf.centrality(args.verbose, args.overwrite, repo)

    if args.dca:
        anlyzgrf.dca(args.verbose, args.overwrite, repo)

    if args.ffiaf:
        anlyzgrf.ffiaf(args.verbose, args.overwrite, repo)


def validate_ignored(ignored, arguments):

    args = get_args(arguments)

    for arg in ignored:
        if arg not in args:
            print("Invalid --ignore arguments! '{}' not recognized. Terminating.".format(arg))
            quit()


def grab_repos():
    repos = []
    config = os.getcwd() + "\\config\\repositories.txt"
    with open(config, encoding='utf-8') as tx:
        for line in tx:
            repo = line.rsplit('/', 1)[-1] # last part of gitURL
            repos.append(repo.rstrip())
    return repos


def get_args(arguments):
    args = str(arguments)
    args = args.replace("Namespace(", "")
    args = re.sub(r"\[.*?\]", '', args)
    args = args.replace("ignore", "")
    args = args.split(', ')
    
    cleanedArgs = []
    for arg in args: 
        clean = arg.split("=")[0]
        cleanedArgs.append(clean)
    cleanedArgs = list(filter(str.strip, cleanedArgs))

    return cleanedArgs


def trueall(args):
    args.combine = True
    args.bicluster = True
    args.centrality = True
    args.dca = True
    args.ffiaf = True
    args.authvuln = True
    args.authbug = True
    args.authflaw = True
    args.authinfluence = True
    args.flaws = True
    args.coworkers = True
    args.lynks = True

    return args


def ignore(args):
    if args.ignore is None:
        return args
    if "combine" in args.ignore:
        args.combine = False
    if "bicluster" in args.ignore:
        args.bicluster = False
    if "centrality" in args.ignore:
        args.centrality = False
    if "dca" in args.ignore:
        args.dca = False
    if "ffiaf" in args.ignore:
        args.ffiaf = False
    if "authvuln" in args.ignore:
        args.authvuln = False
    if "authbug" in args.ignore:
        args.authbug = False
    if "authflaw" in args.ignore:
        args.authflaw = False
    if "authinfluence" in args.ignore:
        args.authinfluence = False
    if "flaws" in args.ignore:
        args.flaws = False
    if "coworkers" in args.ignore:
        args.coworkers = False
    if "lynks" in args.ignore:
        args.lynks = False

    return args


if __name__ == '__main__':
    main()