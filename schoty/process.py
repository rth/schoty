# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import numpy as np




LCL_OPERATIONS = {'^CB RETRAIT': 'cash',
                  '^PRLV SEPA.*': 'debit',
                  '^CHQ\..*': 'cheque',
                  '^CB .+ \d\d/\d\d/\d\d': 'CC',
                  '^VIREMENT.*': 'wire',
                  '^VIR .*': 'wire'
                  }

LCL_OPERATIONS_CLEANUP = [('^CB RETRAIT.*',  'CB RETRAIT'),
                          ('^CB (?P<x>.+) \d\d/\d\d/\d\d', "\g<x>"),
                          ('^CHQ\..*', 'CHQ'),
                          ('^PRLV( SEPA)?(?P<x>.*)', '\g<x>'),
                          ('^(?P<x>VIR(EMENT)?)( SEPA)?( M)? (?P<y>.*)', lambda x: 'VIREMENT ' + x.group('y').upper()),
                          ('^(?P<x>[A-Z\s]{2,40})\s+\d+', '\g<x>'),
                          ('^(ED/)?DIA.*', 'DIA')
                          ]

LCL_OPERATIONS_CLEANUP += [('^(?P<x>{}).*'.format(name), '\g<x>') for name in\
        ['R.gularisation d.bit', 'REM CHQCH', 'MONEO CHGT',
            # 

            # entertainement
            'FNAC', 'UGC', 'MK2'

            # coffe
            'CAFFE NERO',

            # food
            'BURGER KING',

            # flights
            "EASYJET", 'SWISS INT.'

            # transport
            'VELIB',

            # shops
            'PRIMARK', 'WINEMARK', 'CVS PHARMACY', 'CARREFOUR', 'ZARA', 'H & M',
            'MACY*S', 'ATAC'
         #'RYANAIR', 'EASYJET', 'AUCHAN', 'ECHEANCE PRET PERMANENT', 'DECATHLON',
         #   'CAFFE NERO', 'WINEMARK', 'MONOPRIX', 'CVS PHARMACY', 'DARTY',
         #   'DELTA AIR', 'FRANPRIX', 'AERLING', 'SWISS INT.', 'MGEN', 'UGC', 'PRIMARK',
         #   'ED/DIA', 'MK2', 'CARREFOUR', 'DIA', 'MGEN', 'LIBRE COURS', 'R{gularisation d{bit',
         #   'VERSEMENT ESPECES', 'MONEO CHGT', 'BURGER KING', 'UNITED', 'ERAM', '7-ELEVEN',
         #   'ROMANOS', 'AMERICAN AI', 'BHV', 'ELDORADO', 'BEST BUY', 'SMATCH', 'LA POSTE',

            ]]

def detect_operation_type(row):
    for key, op in LCL_OPERATIONS.items():
        if re.match(key, row['descr']):
            return op
    else:
        return 'None'


def simplify_operation_name(row):

    name = row['descr']

    for regexp, expr in LCL_OPERATIONS_CLEANUP:
        if re.match(regexp,  name):
            name = re.sub(regexp, expr, name)
    return name.strip()



def process_statement(df):

    df_out =  df.copy()
    df_out['op_type'] = df.apply(detect_operation_type, axis=1)

    df_out['name'] = df.apply(simplify_operation_name, axis=1)


    return df_out

