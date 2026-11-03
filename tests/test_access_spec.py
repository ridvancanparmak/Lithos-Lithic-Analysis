"""Cross-platform tests against audited original Gürbelen lookup metadata."""
from pathlib import Path
import csv,re,unittest
from lithos.analysis import frequency,label
from lithos.repository import TABLES
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

class TestGurbelenAccessConventions(unittest.TestCase):
 def test_exact_original_tables(self):
  self.assertEqual(TABLES,('ÖZELLİKLER','ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT'))
 def test_glossary_bilingual(self):
  f=ROOT/'veri_sozlugu'/'GURBELEN18_lookup_TR_EN.csv'
  with f.open(encoding='utf-8-sig',newline='') as src:rows=list(csv.DictReader(src))
  self.assertEqual(len(rows),202)
  self.assertEqual(len(rows),len({(r['Table'],r['Field'],r['Turkish']) for r in rows}))
  self.assertTrue(all(r['Table'] in TABLES and r['Turkish'] and r['English'] for r in rows))
  fields={}
  for r in rows:fields.setdefault((r['Table'],r['Field']),[]).append('"'+r['English'].replace('"','""')+'"')
  self.assertTrue(all(len(';'.join(values))<=255 for values in fields.values()))
 def test_access_builder_does_not_shadow_template_path(self):
  # PowerShell treats $TR and $tr as the SAME variable. This regression
  # previously caused a lookup choice (e.g. "Uzun") to replace the .accdb path.
  ps=(ROOT/'ACCESS_SABLON_OLUSTUR.ps1').read_text(encoding='utf-8-sig')
  self.assertIn('foreach($turkishLookupChoice in $values)',ps)
  self.assertIn('Copy-Item -LiteralPath $TurkishTemplatePath -Destination $EnglishTemplatePath',ps)
  self.assertNotRegex(ps,r'(?i)\$(?:TR|EN)\b')
  self.assertNotRegex(ps,r'(?i)foreach\s*\(\s*\$TurkishTemplatePath\b')
  self.assertIn('Test-Path -LiteralPath $TurkishTemplatePath -PathType Leaf',ps)
  self.assertIn("GetExtension($TurkishTemplatePath) -ine '.accdb'",ps)
 def test_english_report_controlled_values(self):
  data=pd.DataFrame({'Hammadde':['Çakmaktaşı','Çakmaktaşı','Radyolarit']})
  counts,_,_=frequency(data,'Hammadde','ÖZELLİKLER','en')
  self.assertEqual(set(counts['category']),{'Flint','Radiolarite'})
  self.assertEqual(label('ÖZELLİKLER','Hammadde','en'),'Raw Material')
 def test_bat_no_bom_and_setup_paths(self):
  for file in ROOT.glob('*.bat'):
   contents=file.read_bytes()
   self.assertFalse(contents.startswith(b'\xef\xbb\xbf'),file.name)
   contents.decode('ascii')
  script=(ROOT/'installer.iss').read_text(encoding='utf-8-sig')
  self.assertIn('SourcePath}dist\\Lithos_v1_0_2\\*',script)
  self.assertIn('SourcePath}assets\\lithos_v102.ico',script)
  ps=(ROOT/'ACCESS_SABLON_OLUSTUR.ps1').read_text(encoding='utf-8-sig')
  self.assertFalse(re.search(r'\$[A-Za-z_][A-Za-z_0-9]*:(?![A-Za-z_])',ps))

if __name__=='__main__':unittest.main()
