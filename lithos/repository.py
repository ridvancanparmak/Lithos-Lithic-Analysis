# -*- coding: utf-8 -*-
"""GURBELEN-18 Access database adapter. No SQLite or invented schema."""
from __future__ import annotations
from pathlib import Path
from contextlib import contextmanager
import shutil,sys
import pandas as pd
from .schema import TABLES,canonical_table

class DatabaseError(Exception): pass


def connect_access(path,readonly=True):
    try:
        import pyodbc
    except ImportError as exc:
        raise DatabaseError('pyodbc is missing; run the Windows setup / pyodbc kurulu değil.') from exc
    driver='Microsoft Access Driver (*.mdb, *.accdb)'
    if driver not in pyodbc.drivers():
        raise DatabaseError('Microsoft Access ODBC/ACE driver missing or incorrect 32/64-bit architecture. Access ODBC/ACE sürücüsü eksik veya mimarisi uyumsuz.')
    connstr=f'DRIVER={{{driver}}};DBQ={Path(path).resolve()};'
    if readonly: connstr+='ReadOnly=1;'
    return pyodbc.connect(connstr,timeout=25,autocommit=False)

def user_template_directory():
    """Writable per-user template cache (independent of read-only installed application)."""
    import os
    appdata=os.environ.get('LOCALAPPDATA')
    return (Path(appdata) if appdata else Path.home()/'.local'/'share')/'Lithos'/'Templates'


def template_path(lang='tr'):
    suffix='_EN' if lang=='en' else ''
    filename=f'Lithos_GURBELEN18_Bos{suffix}.accdb'
    candidates=[user_template_directory()/filename]
    if getattr(sys,'frozen',False):
        candidates += [Path(sys.executable).resolve().parent/'Templates'/filename,
                       Path(getattr(sys,'_MEIPASS',Path(sys.executable).parent))/'Templates'/filename]
    candidates += [Path(__file__).resolve().parents[1]/'Templates'/filename,
                   Path.cwd()/'Templates'/filename]
    return next((p for p in candidates if p.is_file()),None)

def create_database(path,lang='tr'):
    path=Path(path).resolve()
    if path.exists(): raise DatabaseError(f'Output exists / Dosya zaten var: {path}')
    template=template_path(lang)
    if not template:
        raise DatabaseError('Original GURBELEN-18 blank Access template was not created. Run 01_ACCESS_SABLONLARI_OLUSTUR.bat first / Önce 01_ACCESS_SABLONLARI_OLUSTUR.bat çalıştırın.')
    with template.open('rb') as f:
        if b'Standard ACE DB' not in f.read(32):raise DatabaseError('Template is not a genuine .accdb file')
    path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(template,path)
    return path

class DataStore:
    def __init__(self,path):
        self.path=Path(path).resolve()
        if self.path.suffix.lower() not in ('.accdb','.mdb'):
            raise DatabaseError('Lithos uses the original Access format only: .accdb or .mdb')
        if not self.path.is_file():raise FileNotFoundError(str(self.path))
        self.kind='access'
    @contextmanager
    def connection(self,write=False):
        con=connect_access(self.path,readonly=not write)
        try:
            yield con
            if write:con.commit()
        except Exception:
            if write:con.rollback()
            raise
        finally:con.close()
    def tables(self):
        with self.connection() as con:
            cur=con.cursor()
            return [str(x.table_name) for x in cur.tables(tableType='TABLE') if not str(x.table_name).startswith(('MSys','~'))]
    def is_standard(self):
        names={canonical_table(x) for x in self.tables()}
        return set(TABLES).issubset(names)
    def get_table(self,name,limit=None):
        names={x.casefold():x for x in self.tables()}
        real=names.get(str(name).casefold())
        if real is None:
            real=next((actual for actual in names.values() if canonical_table(actual)==canonical_table(name)),None)
        if not real:raise DatabaseError('Table not found: '+str(name))
        if any(c in real for c in '[];\x00'):raise DatabaseError('Unsafe table name')
        select='SELECT '+('TOP '+str(max(1,int(limit)))+' ' if limit else '')+f'* FROM [{real}]'
        with self.connection() as con:
            cur=con.cursor();cur.execute(select)
            columns=[x[0] for x in cur.description]
            rows=[tuple(x) for x in cur.fetchall()]
        return pd.DataFrame.from_records(rows,columns=columns)
    def counts(self):
        result={}
        actual={canonical_table(t):t for t in self.tables()}
        with self.connection() as con:
            cur=con.cursor()
            for t in TABLES:
                real=actual.get(t)
                if not real:raise DatabaseError('Missing original table / Eksik tablo: '+t)
                safe=real.replace(']',']]')
                cur.execute(f'SELECT COUNT(*) FROM [{safe}]')
                result[t]=int(cur.fetchone()[0])
        return result
    def read_for_analysis(self):
        names={x.casefold():x for x in self.tables()}
        canonical={canonical_table(x):x for x in names.values()}
        missing=[x for x in TABLES if x not in canonical]
        if missing:raise DatabaseError('GURBELEN-18 schema mismatch / Orijinal şemaya uymuyor: '+', '.join(missing))
        return {x:self.get_table(canonical[x]) for x in TABLES}
    def terms(self,category,lang='tr'):return []
    def insert(self,*args):raise DatabaseError('Edit records in Microsoft Access; analysis is read-only.')
    def update(self,*args):raise DatabaseError('Edit records in Microsoft Access; analysis is read-only.')
    def delete(self,*args):raise DatabaseError('Edit records in Microsoft Access; analysis is read-only.')

def new_id(prefix):
    import uuid
    return prefix+'-'+uuid.uuid4().hex[:12].upper()
