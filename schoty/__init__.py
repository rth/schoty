# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from ._version import __version__

from .base import open_pdf_statement, BankStatementSerie, process_pdf_statement

from .process import process_statement

from . import _regexp
from .indentify import indentify_pdf_statement



class RegexpDB(object):

    def __init__(self, _regexp):

        data = []

        for backend_name in dir(_regexp):
            if backend_name.startswith('_'):
                continue
            bank_name, lang, statement_type = backend_name.split('_')
            backend = getattr(_regexp, backend_name)
            obj = {key: getattr(backend, key) for key in dir(backend)\
                            if not key.startswith('_')}

            data.append({'bank': bank_name, 'lang': lang, 'kind': statement_type, 'regexp': obj})

            self.data = data


    @property
    def banks(self):
        return [el['bank'] for el in self.data]


    @property
    def langs(self):
        return [el['lang'] for el in self.data]


    def get(self, bank, lang):
        res = self.search(bank, lang)

        if not res:
            raise ValueError('Error: no parser found for bank={}, lang={}'.format(bank, lang))
        elif len(res) == 1:
            return res[0]
        else:
            raise ValueError('This should never occur!')
            


    def search(self, bank=None, lang=None):
        """
        Return a list of items that verify some criteria
        """
        if bank is not None and bank not in self.banks:
            print('Error: user provided bank name {} is not supported!'.format(bank) + \
                  '  Must be one of {}'.format(self.banks))
            return []
        if lang is not None and lang not in self.langs:
            print('Error: user provided lang={} is not supported!'.format(bank) + \
                  '  Must be one of {}'.format(self.langs))
            return []

        if bank is not None and lang is None:
            filt_func = lambda x: x['bank'] == bank
        elif bank is None and lang is not None:
            filt_func = lambda x: x['lang'] == lang
        elif bank is not None and lang is not None:
            filt_func = lambda x: (x['bank'] == bank) and (x['lang'] == lang)
        else:
            filt_func = lambda x: True

        return list(filter(filt_func, self.data))




db = RegexpDB(_regexp)

