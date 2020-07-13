
import argparse
import re
import scripts.oteromakegraphdata as mkgrf
import scripts.oteroanalyzegraphs as anlyzgrf
import scripts.oteroreplace as repc
import scripts.oterocalcdca as calcdca

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", 
                        help="increase output verbosity.",
                        action="store_true")
    
    parser.add_argument("-r", "--runall", 
                        help="run all clone, generative, and analytical functions of program.",
                        action="store_true")

    parser.add_argument("-i", "--ignore", 
                        help="exempt specific clone, generative, or analytical functions of program from --runall. e.g. to exempt biclustering, use '--ignore bicluster'",
                        nargs="+", type=str)

    parser.add_argument("--deleteall", 
                        help="delete all .txt and .xlsx files created by authanalys.py",
                        action="store_true")

    parser.add_argument("-b", "--bicluster", 
                        help="biclustering analysis of authors and code flaws.",
                        action="store_true")

    parser.add_argument("-c", "--clonerepo", 
                        help="download repository to local machine via Git. Specify path to .txt file containt Git URLs.")

    parser.add_argument("-f", "--ffiaf", 
                        help="Flaw-Frequency * Inverse Author Frequency (FFIAF) analysis of authors and code flaws.",
                        action="store_true")

    parser.add_argument("-d", "--dca", 
                        help="degree correlation assortativity (DCA) analysis of coworkers and code flaws.",
                        action="store_true")

    parser.add_argument("-av", "--authvuln", 
                        help="generate .txt of authors and vulnerabillities from raw csv.",
                        action="store_true")

    parser.add_argument("-ab", "--authbug", 
                        help="generate .txt of authors and bugs from raw csv.",
                        action="store_true")       
                        
    parser.add_argument("--flaws", 
                        help="generate .txt of flaws linked by author or by file.",
                        action="store_true")      

    parser.add_argument("--coworkers", 
                        help="generate .txt of coworkers; authors of flaws from the same file.",
                        action="store_true")

    parser.add_argument("--lynks", 
                    help="generate Lynksoft-formatted XLSX of existing .txt files.",
                    action="store_true")


    args = parser.parse_args()
    validated = validate_ignored(args.ignore, args)
    if not validated:
        quit()

    if args.verbose:
        print("Verbose Mode On")

    if args.runall:
        if args.verbose:
            print("Running all functions; ignoring {}".format(args.ignore))
        
    mkgrf.runner(args.verbose, args.ignore)
    anlyzgrf.runner(args.verbose, args.ignore)


    repos = [ 'https://github.com/phpmyadmin/phpmyadmin',
             'https://github.com/drupal/drupal',
             'https://github.com/moodle/moodle']
    

    for repo in repos:
        response = input('Generate graph data for '+repo+'? [y]/n\n')
        if(response == 'y'):
            mkgrf.runner(repo) # phpmyadmin

        response = input('Analyze graph data for '+repo+'? [y]/n\n')
        if(response == 'y'):
            name = repo.rsplit('/', 1)[-1] # last part of gitURL
            anlyzgrf.runner(name)
            
            
    print('Program Complete.')

def validate_ignored(ignored, arguments):
    if len(list(ignored)) == 0:
        return False

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

    for arg in ignored:
        if arg not in cleanedArgs:
            print("Invalid --ignore arguments! '{}' not recognized. Terminating.".format(arg))
            quit()
    
    return True

if __name__ == '__main__':
    main()