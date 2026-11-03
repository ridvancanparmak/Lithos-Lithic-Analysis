"""Platform-independent regression: original Gürbelen columns, bilingual DOCX and pie figures.
The synthetic rows below are NOT included in the blank Access templates.
"""
import tempfile,unittest,zipfile
from pathlib import Path
import pandas as pd
from docx import Document
from lithos import analysis


def fake_frames():
 return {
  'ÖZELLİKLER':pd.DataFrame({
   'Analiz_No':['X01','X02','X03','X04','X05','X06'],
   'Hammadde':['Çakmaktaşı','Radyolarit','Çakmaktaşı','Kalsedon','Çakmaktaşı','Radyolarit'],
   'Patina':['Yok','Beyaz','Yok','Gri','Yok','Beyaz'],
   'Uzunluk':[25,22,20,19,30,28],
  }),
  'ÇEKİRDEKLER':pd.DataFrame({
   'Analiz_No':['C01','C02','C03','C04','C05','C06'],
   'Tip':['Hazırlanmış','Hazırlanmış','Hazırlanmamış','Hazırlanmamış','Hazırlanmış','Hazırlanmamış'],
   'Son_alinan_urun':['Yonga','Dilgi','Yonga','Dilgicik','Dilgi','Dilgicik'],
   'Cikarim_yonu':['Merkezcil','Tek Kutuplu','Merkezcil','Tek Kutuplu','Tek Kutuplu','Çapraz'],
   'Vurma_düzlemi':['Ham','Düz','Ham','Yüzcüklü','Düz','Düz'],
  }),
  'MAKROLİTLER':pd.DataFrame({
   'Analiz_No':['M01','M02','M03','M04','M05','M06'],
   'Tip_listesi':['Düzeltili Yonga','Düzeltili Dilgi','Kenar Kazıyıcı','Düzeltili Yonga','Kenar Kazıyıcı','Düzeltili Dilgi'],
   'Tasimalik':['Yonga','Dilgi','Yonga','Yonga','Yonga','Dilgi'],
   'Duzelti':['Dik','Yarı Dik','Pulcuklu','Pulcuklu','Dik','Pulcuklu'],
   'Duzeltinin_konumu':['Distal','Proksimal','Distal','Proksimal','Distal','Mesial'],
   'Duzeltinin_kapladigi_alan':['İnce','Uzun','İnce','Tüm Yüz','Uzun','Uzun'],
   'Uzunluk':[32,41,48,39,51,45]
  }),
  'MİKROLİT':pd.DataFrame({
   'Analiz_No':['K01','K02','K03','K04','K05','K06'],
   'Tip':['Mikrolit']*6,
   'Alt_tip':['Geometrik','Geometrik','Geometrik','Geometrik','Geometrik','Geometrik'][:2]+['Düz sırtlı','Kavisli','Düz sırtlı','Kavisli'],
   'Tasimalik':['Dilgicik','Yonga','Dilgicik','Dilgicik','Dilgi','Dilgicik']
  })
 }

class TestRestoredPieReport(unittest.TestCase):
 def test_bilingual_pie_charts(self):
  saved=analysis.analysis_tables
  analysis.analysis_tables=lambda source: (fake_frames(),False)
  try:
   with tempfile.TemporaryDirectory() as d:
    for lang in ('tr','en'):
     target=Path(d)/f'Lithos_TEST_{lang}.docx'
     result=analysis.create_report(Path(d)/'synthetic.accdb',target,lang=lang,charts=True,detailed=False)
     self.assertTrue(target.is_file())
     with zipfile.ZipFile(target) as z:
      media=[f for f in z.namelist() if f.startswith('word/media/')]
      self.assertGreaterEqual(len(media),8,f'{lang}: expected bar and restored pie charts')
     doc=Document(target)
     full='\n'.join(p.text for p in doc.paragraphs)
     self.assertIn('Pasta Grafik' if lang=='tr' else 'Pie Chart',full)
     self.assertIn('çapraz pasta grafikler' if lang=='tr' else 'cross-analysis pie charts',full)
     self.assertIn('Veri özeti' if lang=='tr' else 'Data overview',full)
  finally:analysis.analysis_tables=saved

if __name__=='__main__':unittest.main()
