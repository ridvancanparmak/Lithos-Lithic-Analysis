from pathlib import Path
import unittest,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class Release102Tests(unittest.TestCase):
 def test_no_first_run_wizard_or_access_builder(self):
  app=(ROOT/'lithos'/'app.py').read_text('utf-8')
  self.assertNotIn('_welcome_first_run',app)
  self.assertNotIn('_build_missing_templates',app)
  self.assertNotIn('welcome_v101_seen',app)
  self.assertIn('def new_database',app)
  self.assertIn('template_path(language) is None',app)
 def test_mountain_is_high_resolution_and_not_stretched(self):
  with Image.open(ROOT/'assets'/'mountain_header_hidpi.png') as img:
   self.assertGreaterEqual(img.width,2000)
   self.assertGreaterEqual(img.width/img.height,5.8)
   self.assertEqual(img.mode,'RGBA')
  code=(ROOT/'lithos'/'app.py').read_text('utf-8')
  self.assertIn('source_width * height / source_height',code)
  self.assertIn('painter.drawPixmap(target,self.mountain)',code)
 def test_both_access_templates_required_before_build(self):
  bat=(ROOT/'02_PORTABLE_OLUSTUR.bat').read_text('ascii')
  for name in ('Lithos_GURBELEN18_Bos.accdb','Lithos_GURBELEN18_Bos_EN.accdb'):
   self.assertIn(name,bat)
  self.assertIn('01_ACCESS_SABLONLARI_OLUSTUR.bat',bat)
  installer=(ROOT/'installer.iss').read_text('utf-8')
  self.assertIn('SourcePath}dist\Lithos_v1_0_2\*',installer)
  self.assertIn('lithos_v102.ico',installer)
 def test_icon_for_every_windows_target(self):
  for name in ('lithos/app.py','installer.iss','02_PORTABLE_OLUSTUR.bat'):
   self.assertIn('lithos_v102.ico',(ROOT/name).read_text('utf-8'))
 def test_bat_ascii(self):
  for p in ROOT.glob('*.bat'):
   p.read_bytes().decode('ascii')
   self.assertFalse(p.read_bytes().startswith(b'\xef\xbb\xbf'))
if __name__=='__main__':unittest.main()
