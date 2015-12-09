# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

def indentify_pdf_statement(txt, bank=None, lang=None):
    """ Take in a string given by pdftotext and return 
      the bank_name and the lang it can correspond to """

    from . import db

    res = []
    for regexp_row in db.search(bank, lang):
        IDENTIFY_REGEXP = regexp_row['regexp']['IDENTIFY']
        backend_flag = []
        for pattern_line in IDENTIFY_REGEXP:
            row_flag = any((regexp_el in txt for regexp_el in pattern_line))
            backend_flag.append(row_flag)

        if all(backend_flag):
            res.append({'bank': regexp_row['bank'], 'lang': regexp_row['lang']})
    return res
