# -*- coding: utf-8 -*-

from . import _base


IDENTIFY = [('SIREN 954 509 741',),
            ('RELEVE DE COMPTE',),
            ('Crédit Lyonnais-SA',)
            ]

BEGIN_STATEMENT = "^\s*DATE\s+LIBELLE\s+VALEUR\s+DEBIT\s+CREDIT"
INIT_STATEMENT = "^\s*" + _base.DATE_SHORT_GEN + "?\s+ANCIEN SOLDE\s+" + _base.N
FINAL_STATEMENT = "^\s*" + _base.DATE_SHORT_GEN + "?\s+SOLDE EN EUROS\s+" + _base.N
TOTAL_STATEMENT = "^\s*TOTAUX\s+" + _base.N + '\s+' + _base.N_2

REGULAR_STATEMENT = "^\s*" + _base.DATE_SHORT + '\s+' + _base.DESCR + '\s+'\
                             + _base.DATE_LONG + '[\s.]+' + _base.N
REGULAR_STATEMENT_COMMENT = '\s{5,10}\s*' + _base.COMMENT

IGNORE_LINES = ['^.*dit Lyonnais-SA au capital.*', '^\s*RELEVE DE COMPTE\s*', '^\s+Page \d+ / \d+\s+',
        '^\s+$', BEGIN_STATEMENT, '^\s*Indicatif.*Compte.*',
        '^[A-Z\s]+$', # name of the account holder
        '^\s+du\s*\d\d.\d\d.\d\d\d\d\s*au\s*' '.*', # e.g. du 02.10.2015 au 30.10.2015 - N° 82
        '^\s+SOIT EN FRANCS.*',
        TOTAL_STATEMENT, # this already parsed when first reading the file
        # LCL Account statements 2009 to 2011-07
        '^\s+SOUS TOTAL :\s+' + _base.N,
        '^\s+CARTE N° [A-Z0-9]+\s+',
        '^\s+SOLDE INTERMEDIAIRE A FIN\s+',
        ]

DATE = '%d.%m.%y'
