# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from ._version import __version__

from .base import open_pdf_statement, BankStatementSerie

from .process import process_statement

from . import _regexp
from .indentify import indentify_pdf_statement


regexp = []

for backend_name in dir(_regexp):
    if backend_name.startswith('_'):
        continue
    bank_name, lang, statement_type = backend_name.split('_')
    backend = getattr(_regexp, backend_name)
    obj = {key: getattr(backend, key) for key in dir(backend)\
                    if not key.startswith('_')}

    regexp.append({'bank': bank_name, 'lang': lang, 'kind': statement_type, 'regexp': obj})




