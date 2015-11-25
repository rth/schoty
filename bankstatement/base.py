# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# installed from 
# pip install git+https://github.com/drj11/pdftables.git --user
# pip install git+https://github.com/rth/pdftables --user
# pip install git+https://github.com/euske/pdfminer.git --user

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator



from pdftables.pdftables import page_to_tables
from pdftables.display import to_string

import pandas as pd

import re
import numpy as np
from .parsers import LCLMonthlyAccountStatement


def bank_statement( path, bank_name, debug=False, caching=True):

    fh = open(path, 'rb')

    parser = PDFParser(fh)

    doc = PDFDocument(parser, caching=caching)

    # Check if the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Set parameters for analysis.
    laparams = LAParams()
    laparams.word_margin = 0.0
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # finally perform the 
    if bank_name == 'LCL-fr':
        st = LCLMonthlyAccountStatement()
    else:
        raise NotImplementedError
    for idx, page in enumerate(PDFPage.create_pages(doc)):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        
        table_data, table_obj = page_to_tables(layout)

   #     #print('='*20, idx)
   #     st.process_page(table_data, debug=debug)
   #     #  #print(to_string(table.data))
   # st.finalize()

    fh.close()


    return st
