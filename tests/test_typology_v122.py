# -*- coding: utf-8 -*-
"""1.2.2: no manual lookups, bilingual table aliases and parent-denominator analysis."""
import unittest, csv, tempfile
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from lithos.industry import build_industry_tree,flatten_tree,type_detail
from lithos.schema import canonical_table,ENGLISH_TABLES
from lithos.repository import DataStore
from lithos import analysis

ROOT=Path(__file__).resolve().parents[1]

def rows():
    base=pd.DataFrame({'Analiz_No':['A'+str(i) for i in range(1,11)]})
    core=pd.DataFrame({
      'Analiz_No':['C1','C2','C3','C4','C5','C6'],
      'Tip':['Hazırlanmış','Hazırlanmış','Hazırlanmış','Hazırlanmış','Hazırlanmamış','Hazırlanmamış'],
      'Alt_tip':['Recurrent Levallois','Recurrent Levallois','Lineal Levallois','Prizmatik','Şekilsiz','Tek Kutuplu'],
      'Cikarim_yonu':['Merkezcil','İki Kutuplu','Tek Kutuplu','Tek Kutuplu','Düzensiz','Tek Kutuplu'],
      'Alinan_urun_sayisi':[4,8,1,12,3,4],
      'Vurma_düzlemi':['Düz','Yüzcüklü','Düz','Kırık','Ham','Düz'],
    })
    macro=pd.DataFrame({
     'Analiz_No':['M1','M2','M3','M4','M5'],
     'Tip_listesi':['Çentikli Alet','Çentikli Alet','Çentikli Alet','Kenar Kazıyıcı','Kenar Kazıyıcı'],
     'Alt_tip':['Makro Çentikli','Makro Çentikli','Çoklu Çentikli','Yatay İçbükey','Tek Dışbükey'],
     'Tasimalik':['Yonga','Dilgi','Yonga','Yonga','Döküntü'],
     'Duzelti':['Pulcuklu','Dik','Pulcuklu','Yarı Dik','Dik'],
     'Uzunluk':[22,20,21,42,54],
    })
    micro=pd.DataFrame(columns=['Analiz_No','Tip','Alt_tip','Tasimalik'])
    return {'ÖZELLİKLER':base,'ÇEKİRDEKLER':core,'MAKROLİTLER':macro,'MİKROLİT':micro}

class TestTypeCenteredReports(unittest.TestCase):
 def test_hierarchy_counts_and_denominators(self):
  tree=build_industry_tree(rows(),'tr')
  self.assertEqual(tree[0]['count'],6)
  self.assertEqual(tree[0]['base_total'],10)
  self.assertAlmostEqual(tree[0]['base_pct'],60)
  parents={x['raw']:x for x in tree[0]['children']}
  prepared=parents['Hazırlanmış']
  self.assertEqual(prepared['count'],4)
  self.assertAlmostEqual(prepared['parent_pct'],66.7)
  lev=next(n for n in flatten_tree([prepared]) if n['raw']=='__levallois__')
  self.assertEqual(lev['count'],3)
  self.assertAlmostEqual(lev['parent_pct'],75.0)
  typed=tree[1]['children'][0]
  self.assertEqual(typed['count'],5)
  dent=next(n for n in typed['children'] if 'Çentikli' in n['name'])
  self.assertEqual(dent['count'],3)
  self.assertAlmostEqual(dent['parent_pct'],60)
  subtype=next(n for n in dent['children'] if 'Makro' in n['name'])
  self.assertEqual(subtype['count'],2)
  self.assertAlmostEqual(subtype['parent_pct'],66.7)
 def test_type_driven_features(self):
  f=rows();tree=build_industry_tree(f,'en')
  dent=next(n for n in tree[1]['children'][0]['children'] if n['count']==3)
  info=type_detail(f,dent,'en')
  blank=next(x for x in info['fields'] if x['field']=='Tasimalik')
  self.assertEqual(blank['valid'],3)
  self.assertEqual(blank['options'][0]['label'],'Flake')
  self.assertEqual(blank['options'][0]['count'],2)
  self.assertTrue(any(x['name']=='Length' for x in info['metrics']))
 def test_original_and_english_table_aliases(self):
  self.assertEqual(ENGLISH_TABLES['ÖZELLİKLER'],'Features')
  self.assertEqual(canonical_table('Cores'),'ÇEKİRDEKLER')
  self.assertEqual(canonical_table('Macroliths'),'MAKROLİTLER')
  self.assertEqual(canonical_table('Microliths'),'MİKROLİT')
  obj=DataStore.__new__(DataStore)
  english=list(ENGLISH_TABLES.values())
  with patch.object(DataStore,'tables',return_value=english),patch.object(DataStore,'get_table',side_effect=lambda name:pd.DataFrame({'name':[name]})):
   self.assertTrue(obj.is_standard())
   result=obj.read_for_analysis()
   self.assertEqual(list(result),list(ENGLISH_TABLES))
   self.assertEqual(result['ÇEKİRDEKLER'].iloc[0,0],'Cores')
 def test_access_builder_translations_and_browse_flags(self):
  ps=(ROOT/'ACCESS_SABLON_OLUSTUR.ps1').read_text(encoding='utf-8-sig')
  for item in ('Features','Cores','Macroliths','Microliths','English Caption','TableDefs.Item($name)'):
   self.assertIn(item,ps)
  with (ROOT/'veri_sozlugu/GURBELEN18_alan_basliklari_TR_EN.csv').open(encoding='utf-8-sig') as f:
   mapping={(r['Table'],r['Field']):r['EnglishCaption'] for r in csv.DictReader(f)}
  for k,v in {('ÇEKİRDEKLER','Alinan_urun_sayisi'):'Number of Removed Products',
              ('ÇEKİRDEKLER','Donem'):'Period',('MAKROLİTLER','Tasimalik'):'Blank Type',
              ('ÖZELLİKLER','Genişlik'):'Width',('ÖZELLİKLER','Açıklama'):'Description',
              ('ÖZELLİKLER','Çizim'):'Drawing',('ÖZELLİKLER','Patina'):'Patina'}.items():
   self.assertEqual(mapping[k],v)
  ui=(ROOT/'lithos/app.py').read_text(encoding='utf-8')
  self.assertNotIn('self.lang_combo',ui)
  for target in ('flag_tr.png','flag_en.png','lang_tr_btn','lang_en_btn','flagSeparator','QTreeWidget','browse_out.setMinimumWidth(77)','QSizePolicy.Policy.Ignored'):
   self.assertIn(target,ui)
 def test_word_typology_section(self):
  from docx import Document
  with patch.object(analysis,'analysis_tables',return_value=(rows(),True)):
   with tempfile.TemporaryDirectory() as d:
    dest=Path(d)/'report.docx'
    analysis.create_report('demo.accdb',dest,'en',charts=False)
    doc=Document(dest)
    text='\n'.join(x.text for x in doc.paragraphs)
    self.assertIn('Typological distribution of the assemblage',text)
    self.assertIn('Type-led technological analysis',text)
    self.assertIn('Number of Removed Products',text)
    words=' '.join(c.text for table in doc.tables for row in table.rows for c in row.cells)
    self.assertIn('Parent (%)',words)
    self.assertIn('Assemblage (%)',words)
if __name__=='__main__':unittest.main()
