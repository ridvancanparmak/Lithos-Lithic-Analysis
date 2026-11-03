# -*- coding: utf-8 -*-
"""Windows build gate. Fail early if the GUI cannot import, construct or switch language.
No database connection and no Access installation is required for this GUI check.
"""
import os
import sys
import traceback
from pathlib import Path

def check():
    # Never pop up a blocking window during automated packaging checks.
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from .schema import TABLES, TABLE_MAP, SCHEMA_VERSION
    from .repository import DataStore
    from .analysis import create_report, compute_summary
    if TABLES != ('ÖZELLİKLER','ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT'):
        raise AssertionError('Wrong original Gürbelen table identifiers')
    from PySide6.QtWidgets import QApplication
    from .app import LithosWindow
    instance = QApplication.instance()
    owns = instance is None
    app = instance or QApplication(['Lithos','--self-test'])
    app.setOrganizationName('Lithos')
    app.setApplicationName('Lithos')
    window = LithosWindow()
    if window.pages.count() != 5:
        raise AssertionError('Expected five functioning navigation pages')
    window.resize(800,580)
    app.processEvents()
    window.lang_en_btn.click()
    if window.lang != 'en':
        raise AssertionError('English selection did not update application language')
    window.lang_tr_btn.click()
    if window.lang != 'tr':
        raise AssertionError('Turkish selection did not update application language')
    for page in range(5):
        window.switch_page(page)
        app.processEvents()
    window.resize(1300,850)
    app.processEvents()
    window.close()
    return 'PASS: source imports, five GUI pages, TR/EN switching, compact + wide resize'

def main():
    path = None
    if len(sys.argv)>=3 and sys.argv[1]=='--output':
        path=Path(sys.argv[2])
    try:
        result=check()
        status=0
    except BaseException:
        result='FAIL: GUI startup check\n'+traceback.format_exc()
        status=1
    if path is not None:
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(result+'\n',encoding='utf-8')
        except Exception as exc:
            if sys.stderr is not None:
                print('Unable to write smoke result:',repr(exc),file=sys.stderr)
            status=1
    if sys.stdout is not None:
        print(result,flush=True)
    return status

if __name__=='__main__':
    raise SystemExit(main())
