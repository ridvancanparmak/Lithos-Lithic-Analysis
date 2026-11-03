# -*- coding: utf-8 -*-
"""Visual-source regressions: no mock counts or placeholder archaeological drawings."""
import tempfile,unittest
from pathlib import Path
from PIL import Image
from lithos.dashboard import dashboard_counts,make_dashboard_charts
from lithos.i18n import tr
from test_reports import fake_frames

ROOT=Path(__file__).resolve().parents[1]

class VisualV10Tests(unittest.TestCase):
    def test_real_assets_present(self):
        for name in ('handaxe_realistic.png','mountain_header.png','flag_tr.png','flag_en.png','lithos.ico'):
            self.assertGreater((ROOT/'assets'/name).stat().st_size,300)
        with Image.open(ROOT/'assets'/'handaxe_realistic.png') as im:
            self.assertEqual(im.mode,'RGBA')
            self.assertEqual(im.getpixel((0,0))[3],0)

    def test_fake_mock_numbers_not_baked_into_app(self):
        ui=(ROOT/'lithos'/'app.py').read_text('utf-8')
        self.assertNotIn("QLabel('247')",ui)
        self.assertNotIn('ghost_pix',ui)
        self.assertIn('dashboard_counts(self._analysis_frames',ui)
        self.assertIn("setWindowTitle('Lithos')",ui)

    def test_language_dashboard_labels(self):
        for key in ('metric_total','metric_tools','metric_cores','metric_microliths','dashboard_charts','selected_type_details'):
            self.assertNotEqual(tr(key,'tr'),key)
            self.assertNotEqual(tr(key,'en'),key)

    def test_actual_data_driven_charts(self):
        frames=fake_frames();counts,_=dashboard_counts(frames)
        self.assertEqual((counts['total'],counts['cores']), (6,6))
        with tempfile.TemporaryDirectory() as tmp:
            for lang in ('tr','en'):
                charts=make_dashboard_charts(frames,Path(tmp)/lang,lang)
                self.assertGreaterEqual(len(charts),3)
                for name,filename in charts:
                    self.assertTrue(Path(filename).is_file())
                    self.assertGreater(Path(filename).stat().st_size,7000)

    def test_missing_data_no_fake_chart(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(make_dashboard_charts({},tmp,'tr'),[])

if __name__=='__main__':unittest.main()
