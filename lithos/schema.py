# -*- coding: utf-8 -*-
"""Single authoritative table identifiers: the original GURBELEN-18.accdb.

Do not invent field definitions. Actual table structures, data types, relations,
validation and lookup choices are preserved by copying the source Access file.
"""
SCHEMA_VERSION = 'GURBELEN-18-original'
TABLES = ('ÖZELLİKLER', 'ÇEKİRDEKLER', 'MAKROLİTLER', 'MİKROLİT')
ENGLISH_TABLES = {
    'ÖZELLİKLER':'Features',
    'ÇEKİRDEKLER':'Cores',
    'MAKROLİTLER':'Macroliths',
    'MİKROLİT':'Microliths',
}

def canonical_table(name):
    key=str(name).casefold()
    for tr,en in ENGLISH_TABLES.items():
        if key in (tr.casefold(),en.casefold()):return tr
    return str(name)

# No independent relational scheme is imposed over the original Access schema.
TABLE_MAP = {}
VOCABULARY = {}

def field_label(table, field, lang='tr'):
    return str(field).replace('_', ' ')

def term_label(group, code, lang='tr'):
    return str(code)
