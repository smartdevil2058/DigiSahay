import unittest
import time
from datetime import timedelta
from app import app
from extension import db
from model import User
from flask_jwt_extended import create_access_token


class TestAuthFlow(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_01_new_user_entry_redirects_to_auth(self):
        """Unauthenticated visitor at '/' is redirected to dedicated /auth portal."""
        res = self.client.get("/", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/auth", res.headers.get("Location", ""))

    def test_02_dedicated_auth_page_has_no_main_app_navbar(self):
        """The auth page must NOT include main website sidebar, header, or app layout."""
        res = self.client.get("/auth")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Confirm dedicated auth portal elements exist
        self.assertIn("Welcome to DigiSahay", html)
        self.assertIn("Citizen Authentication Portal", html)
        self.assertIn("loginForm", html)
        self.assertIn("registerForm", html)

        # Confirm main website UI components are completely absent
        self.assertNotIn("app-sidebar", html)
        self.assertNotIn("app-header", html)
        self.assertNotIn("mobileMenuTrigger", html)
        self.assertNotIn("sidebar-nav", html)
        self.assertNotIn("Guest Mode", html)

    def test_03_protected_routes_require_authentication(self):
        """All main application routes redirect unauthenticated users to /auth with next."""
        app_routes = [
            "/dashboard",
            "/services",
            "/prerequisite-checker",
            "/centers",
            "/apply",
            "/documents",
            "/applications",
            "/profile",
        ]
        for path in app_routes:
            res = self.client.get(path, follow_redirects=False)
            self.assertEqual(res.status_code, 302)
            loc = res.headers.get("Location", "")
            self.assertIn("/auth", loc)
            self.assertIn("next", loc)

    def test_04_register_new_user(self):
        """Create Account registration endpoint works for a new citizen."""
        test_email = f"citizen_new_{int(time.time())}@example.com"
        res = self.client.post("/api/auth/register", json={
            "email": test_email,
            "password": "StrongPassword123!",
            "preferred_language": "gu"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["email"], test_email)

    def test_05_login_success_sets_cookie_and_token(self):
        """Successful login returns access token and sets HTTP-only session cookie."""
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

    def test_06_valid_session_allows_dashboard_access(self):
        """Valid session automatically opens dashboard and allows app browsing."""
        with app.app_context():
            user = User.query.first()
            self.assertIsNotNone(user)
            token = create_access_token(identity=user.user_id)

        self.client.set_cookie("access_token_cookie", token)

        # Accessing '/' directly continues to /dashboard
        res_root = self.client.get("/", follow_redirects=False)
        self.assertEqual(res_root.status_code, 302)
        self.assertIn("/dashboard", res_root.headers.get("Location", ""))

        # Authenticated user on /dashboard receives 200 with anti-cache headers
        res_dash = self.client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn("no-store", res_dash.headers.get("Cache-Control", ""))

    def test_07_authenticated_user_accesses_app_pages(self):
        """Authenticated user with valid session can access application pages."""
        with app.app_context():
            user = User.query.first()
            token = create_access_token(identity=user.user_id)

        self.client.set_cookie("access_token_cookie", token)

        for path in ["/services", "/prerequisite-checker", "/centers"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)

    def test_08_expired_session_redirects_to_auth_expired(self):
        """Expired session is caught and redirected to /auth?expired=1."""
        with app.app_context():
            user = User.query.first()
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
        """Logout invalidates cookie and redirects user to dedicated /auth?logged_out=1."""
        with app.app_context():
            user = User.query.first()
            token = create_access_token(identity=user.user_id)

        self.client.set_cookie("access_token_cookie", token)

        res = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("logged_out=1", res.headers.get("Location", ""))
        self.assertIn("no-store", res.headers.get("Cache-Control", ""))

        # Accessing protected page after logout redirects to /auth
        res_after = self.client.get("/dashboard", follow_redirects=False)
        self.assertEqual(res_after.status_code, 302)
        self.assertIn("/auth", res_after.headers.get("Location", ""))


if __name__ == "__main__":
    unittest.main()
