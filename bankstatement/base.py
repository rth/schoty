# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import os.path

from .parsers import LCLMonthlyAccountStatement
from subprocess import Popen, PIPE

# http://blog.alivate.com.au/poppler-windows/

DEFAULT_PDFTOTEXT = '/usr/bin/pdftotext'

def bank_statement( path, bank_name, debug=False, work_dir='/tmp/', pdftotext=DEFAULT_PDFTOTEXT,
        hide_matched=False):

    basedir, basename = os.path.split(path)
    basename, _ = os.path.splitext(basename)

    txt_path = os.path.join(work_dir, basename + '.txt')


    p = Popen([pdftotext, '-layout', path, txt_path], stderr=PIPE)

    p.wait()

    # get the right parser
    if bank_name == 'LCL-fr':
        st = LCLMonthlyAccountStatement()
    else:
        raise NotImplementedError

    with open(txt_path, 'rt') as fh:
        txt = fh.readlines()
        for line in txt:
            st.detect_credit_debit_positions(line)
        for line in txt:
             st.process_line(line, debug=debug, hide_matched=hide_matched)


        st.finalize()


    os.remove(txt_path)

    return st
