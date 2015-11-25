# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bankstatement import bank_statement

import pandas as pd

import re
import numpy as np


import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#filepath = '../datasets/LCL_roman/2015/COMPTEDEDEPOTS_00744058275_20151030.pdf'
filepath = '../datasets/LCL_roman/2013/COMPTEDEDEPOTS_00744058275_20131231.pdf'

st = bank_statement(filepath, 'LCL-fr', debug=True, hide_matched=False)

print(st)
#st.data['balance'].plot()
#plt.show()

print(st.data[['datelong', 'descr', 'amount', 'balance']])


#print(res)
