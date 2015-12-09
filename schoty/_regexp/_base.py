# -*- coding: utf-8 -*-

N = "(?P<amount>\d*\s?\d+,\d\d)"
N_2 = "(?P<amount2>\d*\s?\d+,\d\d)" # same think with a different key
DATE_SHORT = "(?P<dateshort>\d\d.\d\d)"
DATE_SHORT_GEN  = "(?P<dateshort>\d\d[\./]\d\d)"
DATE_LONG = "(?P<datelong>\d\d\.\d\d.\d\d)"
DESCR = '(?P<descr>.+)'
COMMENT = '(?P<descr>.{1,40})'
