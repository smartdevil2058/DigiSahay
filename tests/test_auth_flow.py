import unittest
import time
from datetime import timedelta
from app import app
from extension import db
from model import User, Service, ServiceCenter
from flask_jwt_extended import create_access_token


class TestAuthFlow(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_01_new_user_entry_redirects_to_auth(self):
        """Scenario 1: Visitor with no active session visits '/' -> redirected to /auth."""
        res = self.client.get("/", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/auth", res.headers.get("Location", ""))

    def test_02_logged_out_direct_dashboard_redirects(self):
        """Scenario 3: Unauthenticated user accesses /dashboard -> redirected to /auth with next."""
        res = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        loc = res.headers.get("Location", "")
        self.assertIn("/auth", loc)
        self.assertIn("next", loc)

    def test_03_protected_routes_require_auth(self):
        """Scenario 4 & 9: Verify other protected citizen pages redirect."""
        for path in ["/documents", "/applications", "/profile", "/apply"]:
            res = self.client.get(path, follow_redirects=False)
            self.assertEqual(res.status_code, 302)
            self.assertIn("/auth", res.headers.get("Location", ""))

    def test_04_public_routes_accessible_without_auth(self):
        """Scenario 11: Informational pages remain accessible."""
        for path in ["/services", "/prerequisite-checker", "/centers"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)

    def test_05_register_new_user(self):
        """Scenario 10: Create Account flow works for a new user."""
        test_email = f"test_citizen_{int(time.time())}@example.com"
        res = self.client.post("/api/auth/register", json={
            "email": test_email,
            "password": "StrongPassword123!",
            "preferred_language": "gu"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["email"], test_email)

    def test_06_login_success_sets_cookie_and_token(self):
        """Scenario 4: Login sets both JSON token and access cookie."""
        # Use an existing or freshly registered user
        test_email = f"auth_user_{int(time.time())}@example.com"
        self.client.post("/api/auth/register", json={
            "email": test_email,
            "password": "ValidPassword999!",
            "preferred_language": "en"
        })

        res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "ValidPassword999!"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("access_token", data)
        self.assertIn("access_token_cookie", res.headers.get("Set-Cookie", ""))

    def test_07_valid_session_allows_dashboard_access(self):
        """Scenario 4 & 5: Existing user with valid session opens / -> redirects to /dashboard, /dashboard returns 200."""
        with app.app_context():
            user = User.query.first()
            self.assertIsNotNone(user)
            token = create_access_token(identity=user.user_id)

        # Simulate client with cookie
        self.client.set_cookie("access_token_cookie", token)

        # Reopening root '/' should continue directly to /dashboard
        res_root = self.client.get("/", follow_redirects=False)
        self.assertEqual(res_root.status_code, 302)
        self.assertIn("/dashboard", res_root.headers.get("Location", ""))

        # Accessing /dashboard returns 200 and no-store headers
        res_dash = self.client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn("no-store", res_dash.headers.get("Cache-Control", ""))

    def test_08_expired_session_redirects_to_auth_expired(self):
        """Scenario 6: Expired session is rejected and redirected to /auth?expired=1."""
        with app.app_context():
            user = User.query.first()
            # Token with 0 or negative expiration
            expired_token = create_access_token(
                identity=user.user_id,
                expires_delta=timedelta(seconds=-10)
            )

        self.client.set_cookie("access_token_cookie", expired_token)

        res = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        loc = res.headers.get("Location", "")
        self.assertIn("expired=1", loc)

    def test_09_logout_invalidates_session_and_clears_cookie(self):
        """Scenario 7 & 8: Logout unsets cookie and sets anti-cache headers."""
        with app.app_context():
            user = User.query.first()
            token = create_access_token(identity=user.user_id)

        self.client.set_cookie("access_token_cookie", token)

        res = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("logged_out=1", res.headers.get("Location", ""))
        self.assertIn("no-store", res.headers.get("Cache-Control", ""))

        # After logout, accessing dashboard redirects to /auth
        res_after = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(res_after.status_code, 302)
        self.assertIn("/auth", res_after.headers.get("Location", ""))


if __name__ == "__main__":
    unittest.main()
