import unittest
import os
import shutil
import tempfile
from pathlib import Path
from lattice_lock_dashboard.generator import DashboardGenerator

class TestXSSPrevention(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.test_dir, "dashboard.html")
        self.generator = DashboardGenerator()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_xss_prevention(self):
        # Malicious data
        malicious_status = "<script>alert('XSS')</script>"
        malicious_version = '"><img src=x onerror=alert(1)>'
        
        data = {
            "status": malicious_status,
            "version": malicious_version,
            "active_models": 5
        }
        
        self.generator.generate(self.output_path, data)
        
        with open(self.output_path, "r") as f:
            content = f.read()
            
        print("\nGenerated Content:")
        print(content)
        
        # Check that the malicious tags are escaped
        self.assertNotIn("<script>", content)
        self.assertIn("&lt;script&gt;", content)
        self.assertNotIn('"><img', content)
        self.assertIn('&quot;&gt;&lt;img', content)

if __name__ == "__main__":
    unittest.main()
