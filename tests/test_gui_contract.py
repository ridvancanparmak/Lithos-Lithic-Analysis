# -*- coding: utf-8 -*-
"""Regression: application module imports must match original schema API."""
import ast
import unittest
from pathlib import Path
from lithos.schema import TABLES, TABLE_MAP, SCHEMA_VERSION
from lithos.repository import TABLES as REPOSITORY_TABLES

ROOT=Path(__file__).resolve().parents[1]

class TestGUICompatibility(unittest.TestCase):
    def test_original_schema_names(self):
        self.assertEqual(TABLES,REPOSITORY_TABLES)
        self.assertEqual(TABLES,('ÖZELLİKLER','ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT'))
        self.assertTrue(SCHEMA_VERSION)
        self.assertEqual(TABLE_MAP,{})

    def test_all_direct_internal_imports_resolve(self):
        for name in ('app','analysis','repository','preflight'):
            module=ast.parse((ROOT/'lithos'/f'{name}.py').read_text('utf-8'))
            for item in ast.walk(module):
                if not isinstance(item,ast.ImportFrom) or item.level!=1:
                    continue
                source=ROOT/'lithos'/f'{item.module}.py'
                self.assertTrue(source.is_file(),f'{name}: missing {item.module}')
                imported=ast.parse(source.read_text('utf-8'))
                declared=set()
                for node in ast.walk(imported):
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                        declared.add(node.name)
                    if isinstance(node,ast.Assign):
                        for tgt in node.targets:
                            if isinstance(tgt,ast.Name):declared.add(tgt.id)
                    if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name):declared.add(node.target.id)
                    if isinstance(node,(ast.Import,ast.ImportFrom)):
                        for alias in node.names:
                            declared.add(alias.asname or alias.name.split('.')[0])
                for alias in item.names:
                    self.assertIn(alias.name,declared,f'{name}: {item.module}.{alias.name} missing')

    def test_build_requires_real_exe_launch(self):
        script=(ROOT/'02_PORTABLE_OLUSTUR.bat').read_text('ascii')
        self.assertIn('python.exe" -m lithos.preflight',script)
        self.assertIn('Lithos_v1_0_2.exe" --self-test',script)
        self.assertIn('findstr /C:"PASS:"',script)
        install=(ROOT/'03_KURULUM_OLUSTUR.bat').read_text('ascii')
        self.assertIn('GUI_EXE_TESTI.txt',install)

if __name__=='__main__':
    unittest.main()
