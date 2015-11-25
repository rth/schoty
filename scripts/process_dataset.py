# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from bankstatement import bank_statement
from glob import glob

  #filepath = 'data/COMPTEDEDEPOTS_00744058275_20151030.pdf'
  #filepath = 'data/COMPTEDEDEPOTS_00744058275_20131231.pdf'
  
  #st = bank_statement(filepath, 'LCL-fr')

dataset_list = sorted(glob('../datasets/LCL_roman/*/*pdf'))

N_tot = len(dataset_list)
N_valid = 0

print('Processing dataset:')
for path in dataset_list:
    short_path = '-'.join((path[-12:-8],path[-8:-6],path[-6:-4]))
    print(  ' - ', short_path, end='')
    sys.stdout.flush()
    try: 
        st = bank_statement(path, 'LCL-fr')
        N_valid += 1
        print(' ->  [ok]')
    except:
        print(' ->  [failed]')

print('     successfully parsed {}/{} files.'.format(N_valid, N_tot))
        
    


