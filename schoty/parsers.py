# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import pandas as pd

import re
import numpy as np



def _str2num(x):
    return float(x.replace(',','.').replace(' ', ''))

def _num2str(x):
    return '{:,}'.format(x).replace(',', ' ')


def _estimate_sign_pos(pos, credit_column_pos, debit_column_pos, **args):

    d_center = 0.5*(credit_column_pos - debit_column_pos)
    if pos > credit_column_pos - d_center:
        return +1
    else:
        return -1



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



class GenericMonthlyAccountStatement():

    def __init__(self, bank, lang):
        from . import db
        self.pars = {key: None for key in ['initial_statement', 'final_statement',
                                            'total_debit', 'total_credit',
                                            'credit_column_pos', 'debit_column_pos']}
        self.data_raw = []   # contains tuples (date, name, description, debit, credit)
        self.processing_phase = 'head'

        bid = db.get(bank, lang)
        self.regexp = bid['regexp']

    def finalize(self):
        res = pd.DataFrame(self.data_raw)
        res.index = pd.to_datetime(res.apply(lambda row: '.'.join([row['dateshort'],row['datelong'][-2:]]), axis=1))
        res['datelong'] = pd.to_datetime(res.datelong)
        del res['dateshort']
        self.data = res
        self.data['balance'] = self.data['amount'].cumsum() + self.pars['initial_statement']

        if not self._check_validity():
            raise ValueError('Error: failed consistently parsing the BankStatement!')

        #self.calculate_missing_signs()


        #self.final_statement = self.data.balance.values[-1]


    def detect_credit_debit_positions(self, line):
        """ Parsing the document the first time to get the position of the 
        debit and credit columns
        """
        rg = self.regexp
        if self.pars['total_debit'] is not None:
            return
            
        gr = lambda x: res.group(x)
        res = re.match(rg['TOTAL_STATEMENT'], line)
        if res:
            self.pars['total_debit'] = _str2num(gr('amount'))
            self.pars['total_credit'] = _str2num(gr('amount2'))
            self.pars['debit_column_pos'] = res.end('amount')
            self.pars['credit_column_pos'] = res.end('amount2')


    def _check_validity(self):
        is_valid = True

        final_statement_2 = self.pars['total_credit'] - self.pars['total_debit'] 
        err = self.pars['final_statement'] - final_statement_2
        if not np.abs(err) <= 0.01:
            print('Check failed: total_credit - total_debit - final_statement != 0')
            print('             {:.2f}  - {:.2f} - {:.2f} != 0'.format(
                        self.pars['total_credit'],
                        self.pars['total_debit'], self.pars['final_statement']))
            print('               err = {:.2f} euros'.format(err))
            is_valid = False

        amounts = self.data.amount

        total_debit = - self.pars['total_debit']
        if self.pars['initial_statement'] < 0:
            total_debit += - self.pars['initial_statement']
        isum = amounts[amounts<0].sum()
        err = isum - total_debit
        if not np.abs(err) <= 0.01:
            print('Check failed: Sigma debit_i  - total_debit != 0')
            print('              {:.2f} - {:.2f} != 0'.format(isum, total_debit))
            print('               err = {:.2f} euros'.format(err))
            is_valid = False



        total_credit = self.pars['total_credit']
        if self.pars['initial_statement'] > 0:
            total_credit += - self.pars['initial_statement']
        isum = amounts[amounts>0].sum()
        err = total_credit - isum
        if not np.abs(err) <= 0.01:
            print('Check failed: Sigma credit_i - total_credit != 0')
            print('              {:.2f} - {:.2f} != 0'.format(isum, total_credit))
            print('               err = {:.2f} euros'.format(err))
            is_valid = False



        return is_valid

    @property
    def start_date(self):
        return self._get_start_end_date(idx=0)

    @property
    def end_date(self):
        return self._get_start_end_date(idx=-1)


    def _get_start_end_date(self, idx=0):
        dates_short = self.data.dateshort.values

        if idx == 0:
            par_key = 'start_date'
        elif idx == -1:
            par_key = 'end_date'
        else:
            raise ValueError

        if par_key in self.pars:
            dd_mm = self.pars[par_key]
        else:
            dd_mm = dates_short[idx]

        return dd_mm


    def process_line(self, line, debug=False, hide_matched=True):
        """ Parsing the file a second time """
        rg = self.regexp


        if self.processing_phase == 'head' and re.match(rg['BEGIN_STATEMENT'], line):
            self.processing_phase = 'body'
            return


        if self.processing_phase in ['head', 'tail']:
            return

        ignore_line = False
        for regexp in rg['IGNORE_LINES']:
            if re.match(regexp, line):
                ignore_line = True


        if not ignore_line:
            if debug and not hide_matched:
                print(line.replace('\n',''))

            for pattern_name, regexp in [
                    ('initial_statement', rg['INIT_STATEMENT']),
                    ('final_statement',  rg['FINAL_STATEMENT']),
                    ('regular_line',  rg['REGULAR_STATEMENT']),
                    ('regular_line_comment', rg['REGULAR_STATEMENT_COMMENT'])
                    ]:
                if regexp is None:
                    continue

                res = re.match(regexp, line)
                if res:
                    gr = lambda x: res.group(x)
                    if pattern_name in ['initial_statement', 'final_statement']:
                        amount = _str2num(gr('amount'))
                        sign = _estimate_sign_pos(res.end('amount'), **self.pars)
                        self.pars[pattern_name] = amount*sign
                        if 'descr' in res.groupdict():
                            if pattern_name == 'initial_statement':
                                self.pars['start_date'] = gr('descr').replace('/', '.')
                            else:
                                self.pars['end_date'] = gr('descr').replace('/', '.')

                    elif pattern_name == 'regular_line':
                        out = {key: gr(key) for key in ['amount', 'dateshort', 'datelong', 'descr']}

                        amount = _str2num(out['amount']) 
                        sign = _estimate_sign_pos(res.end('amount'), **self.pars)
                        out['amount'] =  amount*sign
                        out['descr'] = out['descr'].strip()
                        out['comment'] = []

                        self.data_raw.append(out)
                    elif pattern_name == 'regular_line_comment' and self.data_raw:
                        prev_el = self.data_raw[-1]
                        prev_el['comment'].append(gr('descr').strip())
                    if debug and not hide_matched:
                        print('        => matched <= ')
                    break
            else:
                if debug and hide_matched:
                    print(line.replace('\n',''))


        if self.processing_phase == 'body' and re.match(rg['FINAL_STATEMENT'], line):
            self.processing_phase = 'tail'


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


    def __repr__(self):
        return str(self.pars)

