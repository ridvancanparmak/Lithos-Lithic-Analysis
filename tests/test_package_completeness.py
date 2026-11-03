# -*- coding: utf-8 -*-
"""Build package checks. Blank Access templates are expected after Windows preparation."""
from pathlib import Path
import os
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_TEMPLATES={
    'Lithos_GURBELEN18_Bos.accdb',
    'Lithos_GURBELEN18_Bos_EN.accdb',
}

class PackageCompletenessTests(unittest.TestCase):
    def test_all_bat_inputs_exist(self):
        for rel in ('requirements.txt','KULLANIM_TR_EN.txt','VERSIYON_NOTLARI.txt',
                    'ACCESS_SABLON_OLUSTUR.ps1','installer.iss','lithos/app.py',
                    'assets/lithos_v102.ico','veri_sozlugu/GURBELEN18_lookup_TR_EN.csv'):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT/rel).is_file(),f'Missing build input: {rel}')

    def test_requirements_match_imports(self):
        req=(ROOT/'requirements.txt').read_text('ascii')
        for package in ('PySide6','pandas','matplotlib','python-docx','pyodbc','Pillow'):
            self.assertIn(package,req)

    def test_bat_has_fail_fast_and_fully_qualified_requirements(self):
        bat=(ROOT/'02_PORTABLE_OLUSTUR.bat').read_text('ascii')
        self.assertIn('if not exist "%~dp0requirements.txt" goto :missing_inputs',bat)
        self.assertIn('-r "%~dp0requirements.txt"',bat)
        self.assertIn('if errorlevel 1 goto :fail',bat)

    def test_only_expected_access_templates_are_present(self):
        """Empty TR+EN .accdb files must be ALLOWED, never mistaken for private data.

        Before template creation, neither exists. After generation, both exist.
        Any third Access file in Templates is forbidden by packaging contract.
        The original GURBELEN-18.accdb may be beside build BAT as input;
        it is not packaged into the executable or portable distribution.
        """
        folder=ROOT/'Templates'
        actual={p.name for p in folder.glob('*.accdb')}
        self.assertFalse(actual-EXPECTED_TEMPLATES,
                         f'Unexpected Access files in Templates: {sorted(actual-EXPECTED_TEMPLATES)}')
        self.assertIn(len(actual),(0,2),
                      'Both Turkish and English empty templates must be created together.')
        if actual:
            self.assertEqual(actual,EXPECTED_TEMPLATES)
            for name in sorted(EXPECTED_TEMPLATES):
                path=folder/name
                self.assertGreater(path.stat().st_size,32,name)
                with path.open('rb') as fp:
                    header=fp.read(32)
                self.assertIn(b'Standard ACE DB',header,
                              f'{name} is not a genuine ACE/Access database.')

    def test_portable_distributes_only_whitelisted_access_templates(self):
        bat=(ROOT/'02_PORTABLE_OLUSTUR.bat').read_text('ascii')
        self.assertNotIn('Templates\\*.accdb',bat,
                         'Do not bundle unrecognized databases with a wildcard.')
        for name in EXPECTED_TEMPLATES:
            self.assertIn('Templates\\'+name,bat)
        self.assertIn('for %%F in ("Templates\\Lithos_GURBELEN18_Bos.accdb" '
                      '"Templates\\Lithos_GURBELEN18_Bos_EN.accdb")',bat)

    @unittest.skipUnless(os.name=='nt','Access/DAO inventory validation requires Windows.')
    def test_created_templates_are_empty_in_access_dao(self):
        """On the target Windows PC, inspect real data in the original 4 tables."""
        folder=ROOT/'Templates'
        actual={p.name for p in folder.glob('*.accdb')}
        if not actual:
            self.skipTest('Template generation has not run yet.')
        script=ROOT/'tests'/'verify_empty_access_templates.ps1'
        self.assertTrue(script.is_file())
        proc=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive',
                             '-ExecutionPolicy','Bypass','-File',str(script),
                             '-TemplateDir',str(folder)],
                            capture_output=True,text=True,timeout=80)
        self.assertEqual(proc.returncode,0,
                         f'Blank Access template verification failed:\n{proc.stdout}\n{proc.stderr}')
        self.assertIn('PASS: TR and EN inventory tables are empty',proc.stdout)

if __name__=='__main__':
    unittest.main()
