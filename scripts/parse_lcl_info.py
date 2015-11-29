# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from schoty import open_pdf_statement, indentify_pdf_statement
import schoty._regexp

import pandas as pd

import sys
import re
import os.path
import numpy as np
from glob import glob


import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#filepath = '../datasets/LCL_roman/2015/COMPTEDEDEPOTS_00744058275_20151030.pdf'
#filepath = '../datasets/LCL_roman/2013/COMPTEDEDEPOTS_00744058275_20131231.pdf'
pattern = os.path.join(sys.argv[1], 'datasets/*/*/*.pdf')
path_list = list(glob(pattern))

pattern = os.path.join(sys.argv[1], 'datasets/*/*/*.pdf')
path_list += list(glob(pattern))


for path in path_list:

    print('{:120} => '.format(path), end='')
    sys.stdout.flush()
    txt = open_pdf_statement(path)

    res = indentify_pdf_statement(txt)
    if len(res) == 1:
        print(res[0]['bank'])
    elif len(res) > 1:
        print('MULTIPLE')
    else:
        print('FALSE')




#print(os.path.abspath(filepath))
#st = open_pdf_statement(filepath, 'LCL', lang='fr', debug=True, hide_matched=False)

#print(st)
#st.data['balance'].plot()
#plt.show()

#print(st.data[['datelong', 'descr', 'amount', 'balance']])


#print(res)
