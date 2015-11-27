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

N_REGEXP = "(?P<amount>\d*\s?\d+,\d\d)"
N_REGEXP2 = "(?P<amount2>\d*\s?\d+,\d\d)" # same think with a different key
DATE_SHORT_REGEXP = "(?P<dateshort>\d\d.\d\d)"
DATE_SHORT_GEN_REGEXP  = "(?P<dateshort>\d\d[\./]\d\d)"
DATE_LONG_REGEXP = "(?P<datelong>\d\d\.\d\d.\d\d)"
DESCR_REGEXP = '(?P<descr>.+)'
COMMENT_REGEXP = '(?P<descr>.{1,40})'

BEGIN_STATEMENT_REGEXP = "^\s*DATE\s+LIBELLE\s+VALEUR\s+DEBIT\s+CREDIT"


INIT_STATEMENT_REGEXP = "^\s*" + DATE_SHORT_GEN_REGEXP + "?\s+ANCIEN SOLDE\s+" + N_REGEXP
FINAL_STATEMENT_REGEXP = "^\s*" + DATE_SHORT_GEN_REGEXP + "?\s+SOLDE EN EUROS\s+" + N_REGEXP
TOTAL_STATEMENT_REGEXP = "^\s*TOTAUX\s+" + N_REGEXP + '\s+' + N_REGEXP2
REGULAR_STATEMENT_REGEXP = "^\s*" + DATE_SHORT_REGEXP + '\s+' + DESCR_REGEXP + '\s+'\
                             + DATE_LONG_REGEXP + '[\s.]+' + N_REGEXP
REGULAR_STATEMENT_COMMENT_REGEXP = '\s{5,10}\s*' + COMMENT_REGEXP

IGNORE_LINES = ['^.*dit Lyonnais-SA au capital.*', '^\s*RELEVE DE COMPTE\s*', '^\s+Page \d+ / \d+\s+',
        '^\s+$', BEGIN_STATEMENT_REGEXP, '^\s*Indicatif.*Compte.*',
        '^[A-Z\s]+$', # name of the account holder
        '^\s+du\s*\d\d.\d\d.\d\d\d\d\s*au\s*' '.*', # e.g. du 02.10.2015 au 30.10.2015 - N° 82
        '^\s+SOIT EN FRANCS.*',
        TOTAL_STATEMENT_REGEXP, # this already parsed when first reading the file
        # LCL Account statements 2009 to 2011-07
        '^\s+SOUS TOTAL :\s+' + N_REGEXP,
        '^\s+CARTE N° [A-Z0-9]+\s+',
        '^\s+SOLDE INTERMEDIAIRE A FIN\s+',
        ]


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



class LCLMonthlyAccountStatement():

    def __init__(self, lang='fr'):
        self.pars = {key: None for key in ['initial_statement', 'final_statement',
                                            'total_debit', 'total_credit',
                                            'credit_column_pos', 'debit_column_pos']}
        self.data_raw = []   # contains tuples (date, name, description, debit, credit)
        self.processing_phase = 'head'
        if lang != 'fr':
            raise NotImplementedError

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
        if self.pars['total_debit'] is not None:
            return
            
        gr = lambda x: res.group(x)
        res = re.match(TOTAL_STATEMENT_REGEXP, line)
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
        if self.processing_phase == 'head' and re.match(BEGIN_STATEMENT_REGEXP, line):
            self.processing_phase = 'body'
            return


        if self.processing_phase in ['head', 'tail']:
            return

        ignore_line = False
        for regexp in IGNORE_LINES:
            if re.match(regexp, line):
                ignore_line = True


        if not ignore_line:
            if debug and not hide_matched:
                print(line.replace('\n',''))

            for pattern_name, regexp in [
                    ('initial_statement', INIT_STATEMENT_REGEXP),
                    ('final_statement',  FINAL_STATEMENT_REGEXP),
                    ('regular_line',  REGULAR_STATEMENT_REGEXP),
                    ('regular_line_comment', REGULAR_STATEMENT_COMMENT_REGEXP)
                    ]:
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


        if self.processing_phase == 'body' and re.match(FINAL_STATEMENT_REGEXP, line):
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

