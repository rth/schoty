# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import pandas as pd

import re
import numpy as np



def _clean_num(x):
    return float(x.replace(',','.').replace(' ', ''))

nregxp = "(\d*\s?\d+,\d\d)"
descr_regexp = '.+'


def optimize_binary(values, sum_p, sum_n):
    import itertools
    # find rows corresponding to the credit
    sign_matrix = np.array(list(itertools.product([0, 1], repeat=len(values))))

    output = (sign_matrix * values[None, :]).sum(axis=1)

    mask = np.abs(output - sum_p) < 0.01
    idx = np.nonzero(mask)[0][0]

    signs = sign_matrix[idx, :]
    signs[signs==0] = -1

    # now verify the debit line
    err = ((signs * values)[signs<0].sum() + sum_n)

    sucess = err < 0.01
    #print('shape', signs.shape)
    return signs[0], signs[1:], sucess, err



class LCLMonthlyAccountStatement():

    def __init__(self):
        self.initial_statement = None
        self.final_statement = None
        self.total_debit = None
        self.total_credit = None
        self.data_raw = []   # contains tuples (date, name, description, debit, credit)
        self.processing_phase = 'head'

    def finalize(self):
        res = pd.DataFrame(self.data_raw)
        res.index = res.date_init
        del res['date_init']
        self.data = res
        self.calculate_missing_signs()

        #print(self.initial_statement)
        self.data['amount_signed'] = self.data['amount']*self.data['sign']
        self.data['balance'] = self.data['amount_signed'].cumsum() + self.initial_statement
        
        self.final_statement = self.data.balance.values[-1]

    def calculate_missing_signs(self):
        signs = self.data.sign.values
        amounts = self.data.amount.values

        mask_missing = np.isnan(signs)
        
        known_credit = amounts[signs>0].sum()
        known_debit = amounts[signs<0].sum()

        prev_statement_sign, opt_signs, success, err  = optimize_binary(
                np.concatenate( (np.array([self.initial_statement]), amounts[mask_missing])), 
                self.total_credit - known_credit,
                self.total_debit - known_debit)

        if success:
            #print('Prev_sign', prev_statement_sign)
            self.initial_statement *= prev_statement_sign
            #print(amounts[mask_missing])
            #print(opt_signs)
            signs[mask_missing] = opt_signs
        else:
            print('Failed to build the balance sheet: {} euro off'.format(err))

        self.data['sign'] = signs






    def process_page(self, table, debug=False):
        for row_orig in table:
            row = ''.join(row_orig)
            if self.processing_phase == 'head' and 'ANCIEN SOLDE' in row:
                self.processing_phase = 'body'
            if 'LCL vous informe sur' in row:
                self.processing_phase = 'tail'

            if self.processing_phase in ['head', 'tail']:
                continue


            if debug:
                print(row_orig)
            for pattern_name, regexp in [
                    ('initial_statement', '^\s*ANCIEN SOLDE\s+' + nregxp),
                    ('total_debit_credit', '^\s*TOTAUX\s+'+ nregxp +'\s+' + nregxp),
                    ('regular_line', '^(\d\d\.\d\d)\s*('+ descr_regexp +')\s*(\d\d\.\d\d.\d\d)\s+'+nregxp+'.*'),
                    ('regular_line_fail', '^(\d\d\.\d\d)\s*('+ descr_regexp +')\s+'+nregxp+'.*')
                    ]:
                res = re.match(regexp, row)
                if res:
                    gr = res.groups()
                    if pattern_name == 'initial_statement':
                        self.initial_statement = _clean_num(gr[0])
                    elif pattern_name == 'total_debit_credit':
                        self.total_debit = _clean_num(gr[0])
                        self.total_credit = _clean_num(gr[1])
                    elif pattern_name in ['regular_line', 'regular_line_fail']:
                        if "LCL vous informe sur" in row:
                            break
                        if pattern_name == 'regular_line':
                            out = {'date_init': gr[0], 'description': gr[1][:50],
                                        'date': gr[2], 'amount': _clean_num(gr[3])}
                        else:
                            out = {'date_init': gr[0], 'description': gr[1][:50],
                                        'date': np.nan, 'amount': _clean_num(gr[2])}

                        out['sign'] = np.nan
                        if len(row_orig) >= 3:
                            if re.match("^\s+"+ nregxp +'\s*', row_orig[-1])  and not row_orig[-2]:
                                out['sign'] = +1
                            elif re.match("^\s+"+ nregxp +'\s*', row_orig[-2])  and not row_orig[-1]:
                                out['sign'] = -1


                        self.data_raw.append(out)
                        if debug:
                            print('         matched')
                    break


    def __repr__(self):

        mdict = {key: getattr(self, key) for key in ['initial_statement', 
                                        'total_debit', 'total_credit'] \
                        if getattr(self, key) is not None}

        return str(mdict)

