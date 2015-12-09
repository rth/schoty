# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import sys
import os.path
from glob import glob

from subprocess import Popen, PIPE

import pandas as pd

from .parsers import GenericMonthlyAccountStatement
from .indentify import indentify_pdf_statement 

# http://blog.alivate.com.au/poppler-windows/
DEFAULT_PDFTOTEXT = '/usr/bin/pdftotext'

class BankStatementSerie(object):
    def __init__(self, path, bank_name, lang='fr', verbose=False, work_dir='/tmp/', 
                    pdftotext=DEFAULT_PDFTOTEXT):
        """ Path can be a glob expression """
        dataset_list = sorted(glob(path))

        # parse serie
        N_tot = len(dataset_list)
        N_valid = 0
        self.elements = []
        if verbose:
            print('Processing dataset:')
        for path in dataset_list:
            short_path = '-'.join((path[-12:-8],path[-8:-6],path[-6:-4]))
            if verbose:
                print(  ' - ', short_path, end='')
                sys.stdout.flush()
            try: 
                st = bank_statement(path, bank_name, lang=lang, pdftotext=pdftotext)
                self.elements.append(st)
                N_valid += 1
                if verbose:
                    print(' ->  [ok]')
            except:
                if verbose:
                    print(' ->  [failed]')

        if verbose:
            print('     successfully parsed {}/{} files.'.format(N_valid, N_tot))

        self._assemble_statements()

    def _assemble_statements(self):
        self.data = pd.concat([el.data for el in self.elements], axis=0)



def open_pdf_statement(path, pdftotext=DEFAULT_PDFTOTEXT):


    p = Popen([pdftotext, '-layout', path, '-'], stderr=PIPE, stdout=PIPE)

    stdout, sterr = p.communicate()

    stdout = stdout.decode("utf-8") 

    return stdout



def process_pdf_statement(path, bank_name=None, lang=None, debug=False, pdftotext=DEFAULT_PDFTOTEXT,
        hide_matched=False):
    from . import db


    txt = open_pdf_statement(path, pdftotext=pdftotext)

    b_pars = indentify_pdf_statement(txt, bank=bank_name, lang=lang)

    if len(b_pars) == 1:
        b_pars = b_pars[0]
    else:
        raise ValueError

    txt = txt.splitlines()


    # get the right parser
    st = GenericMonthlyAccountStatement(**b_pars)

    for line in txt:
        st.detect_credit_debit_positions(line)
    for line in txt:
         st.process_line(line, debug=debug, hide_matched=hide_matched)


    st.finalize()

    return st
