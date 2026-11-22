import unittest
from app import app
from model import ServiceCenter

class TestServiceCenterFix(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = app.test_client()

    def test_database_and_model_coordinates(self):
        with self.app.app_context():
            centers = ServiceCenter.query.all()
            self.assertGreater(len(centers), 0, "No service centers found in database")
            for c in centers:
                self.assertEqual(c.contact_number, "1234567890", f"Center {c.center_id} has wrong contact number: {c.contact_number}")
                self.assertTrue(c.has_valid_coordinates, f"Center {c.center_id} does not have valid coordinates")
                self.assertIsNotNone(c.google_maps_url, f"Center {c.center_id} missing Google Maps URL")
                self.assertTrue(c.google_maps_url.startswith(f"https://www.google.com/maps?q={c.latitude},{c.longitude}"))
                self.assertNotIn("search/?api=1&query=", c.google_maps_url)

    def test_api_endpoint(self):
        res = self.client.get("/api/centers")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        centers = data["centers"]
        self.assertGreater(len(centers), 0)
        for c in centers:
            self.assertEqual(c["contact_number"], "1234567890")
            self.assertTrue(c["has_valid_coordinates"])
            self.assertIn(f"https://www.google.com/maps?q={c['latitude']},{c['longitude']}", c["google_maps_url"])

    def test_html_view(self):
        res = self.client.get("/centers")
        self.assertEqual(res.status_code, 200)
        html = res.text
        self.assertIn("1234567890", html)
        self.assertIn("Open in Google Maps", html)
        with self.app.app_context():
            centers = ServiceCenter.query.all()
            for c in centers:
                self.assertIn(f"{c.latitude},{c.longitude}", html)
                self.assertIn(c.address_line, html)

if __name__ == "__main__":
    unittest.main()
