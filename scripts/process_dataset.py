# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from schoty import BankStatementSerie

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#filepath = 'data/COMPTEDEDEPOTS_00744058275_20151030.pdf'
#filepath = 'data/COMPTEDEDEPOTS_00744058275_20131231.pdf'

#st = bank_statement(filepath, 'LCL-fr')

dataset_list = '../datasets/LCL_roman/*/*pdf'


res = BankStatementSerie(dataset_list, 'LCL', lang='fr', verbose=False)


#print(res.data)

#res.data.balance.plot(
#        xlim=( pd.Timestamp('2014-01-01'), pd.Timestamp('2015-01-01')),
#        ylim=(-1000, 3000))
#
#plt.show()

res.data.to_pickle('LCL_roman.pkl')

