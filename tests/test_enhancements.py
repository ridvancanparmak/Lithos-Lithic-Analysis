# -*- coding: utf-8 -*-
import tempfile, unittest, zipfile, re
from pathlib import Path
from unittest.mock import patch
from docx import Document
from lithos import analysis
from test_reports import fake_frames
class NewLithosRegressions(unittest.TestCase):
 def test_all_fields_not_first_five(self):
  f=fake_frames()
  # Table with many different categories; no five-variable truncation.
  f['MAKROLİTLER']['Dönem']=['Alt-Orta Paleolitik']*6
  result=analysis.generate_observations(f,'en')
  self.assertTrue(any('Period' in x for x in result['MAKROLİTLER']))
  self.assertTrue(any('Retouch' in x for x in result['MAKROLİTLER']))
 def test_original_glossary_supplement(self):
  self.assertEqual(analysis.localize_category('MAKROLİTLER','Tasimalik','Yonga','en'),'Flake')
  self.assertEqual(analysis.localize_category('MAKROLİTLER','Alt_tip','Makro çentikli','en'),'Macronotched tool')
  self.assertEqual(analysis.localize_category('MAKROLİTLER','Donem','Alt-Orta Paleolitik','en'),'Lower–Middle Palaeolithic')
 def test_case_variants_merge_source_intact(self):
  import pandas as pd
  df=pd.DataFrame({'Tasimalik':['Döküntü','döküntü','Yonga']})
  freqs,_,n=analysis.frequency(df,'Tasimalik','MAKROLİTLER','en')
  self.assertEqual(n,3)
  self.assertEqual(len(freqs),2)
  self.assertEqual(int(freqs.iloc[0]['count']),2)
  self.assertEqual(df.Tasimalik.iloc[1],'döküntü')
 def test_gui_chart_previews_include_cross_pies(self):
  with patch.object(analysis,'analysis_tables',return_value=(fake_frames(),False)):
   with tempfile.TemporaryDirectory() as d:
    charts=analysis.make_chart_preview('fake.accdb',d,'en',max_charts=22)
    self.assertGreaterEqual(len(charts),6)
    self.assertGreaterEqual(sum('pie' in Path(p).name for p in charts),3)
    self.assertTrue(all(Path(p).stat().st_size>1000 for p in charts))
 def test_full_english_report(self):
  with patch.object(analysis,'analysis_tables',return_value=(fake_frames(),False)):
   with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'report.docx'
    analysis.create_report('fake.accdb',p,'en',charts=True,detailed=True)
    doc=Document(p)
    self.assertTrue(any(x.text=='Overall data-derived findings' for x in doc.paragraphs))
    assert len(doc.inline_shapes)>=3
    cat=[cell.text for table in doc.tables for row in table.rows for cell in row.cells]
    self.assertIn('Flake',cat)
    self.assertNotIn('Yonga',cat)
if __name__=='__main__':unittest.main()
