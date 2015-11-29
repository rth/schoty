# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from schoty import open_pdf_statement

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
print(sys.argv[1])
filepath = glob(os.path.join(sys.argv[1], 'datasets/LCL/*/2011/*20110601*.pdf'))[0]

print(os.path.abspath(filepath))
st = open_pdf_statement(filepath, 'LCL', lang='fr', debug=True, hide_matched=False)

print(type(st))
#st.data['balance'].plot()
#plt.show()

print(st.data[['datelong', 'descr', 'amount', 'balance']])


#print(res)
