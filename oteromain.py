# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 18:50:33 2020

@author: damon
"""
import oteromakegraphdata as mkgrf
import oteroanalyzegraphs as anlyzgrf
import oteroreplace as repc
import oterocalcdca as calcdca
def main():
    print('start')    



    repos = [ 'https://github.com/phpmyadmin/phpmyadmin',
             'https://github.com/drupal/drupal',
             'https://github.com/moodle/moodle']
    
    
    for repo in repos:
        calcdca.runner(repo)

    quit()

    for repo in repos:
        response = input('Generate graph data for '+repo+'? [y]/n\n')
        if(response == 'y'):
            mkgrf.runner(repo) # phpmyadmin

        response = input('Analyze graph data for '+repo+'? [y]/n\n')
        if(response == 'y'):
            name = repo.rsplit('/', 1)[-1] # last part of gitURL
            anlyzgrf.runner(name)
            
            
    print('Program Complete.')

if __name__ == '__main__':
    main()