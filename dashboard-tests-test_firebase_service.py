import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from dashboard.services.firebase_service import FirebaseService


class FirebaseServiceTests(unittest.TestCase):
    def test_existing_local_cache_is_extended_without_overwriting_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "firestore_local.json"
            cache_path.write_text(json.dumps({
                "users": {"USR_RES_1": {"userId": "USR_RES_1", "name": "Existing Name"}},
                "houses": {"H101": {"houseId": "H101", "residentName": "Existing Name"}},
            }), encoding="utf-8")
            service = object.__new__(FirebaseService)
            service.local_cache_file = str(cache_path)

            service._ensure_local_cache()
            cached = json.loads(cache_path.read_text(encoding="utf-8"))

        self.assertEqual(len(cached["houses"]), 20)
        self.assertEqual(cached["users"]["USR_RES_1"]["name"], "Existing Name")
        self.assertEqual(cached["houses"]["H101"]["residentName"], "Existing Name")
        self.assertIn("USR_RES_20", cached["users"])

    def test_firebase_login_resolves_known_demo_profile_when_cache_is_old(self):
        service = object.__new__(FirebaseService)
        service.api_key = "test-key"
        response = Mock(status_code=200)
        response.json.return_value = {"idToken": "token", "localId": "firebase-user"}

        with patch("dashboard.services.firebase_service.requests.post", return_value=response):
            with patch.object(service, "get_collection", return_value=[]):
                ok, user, message = service.authenticate_user(
                    "resident120@aquanest.test",
                    "password123",
                )

        self.assertTrue(ok)
        self.assertEqual(user["houseId"], "H120")
        self.assertEqual(user["name"], "Aditya Verma")
        self.assertIn("successful", message)


if __name__ == "__main__":
    unittest.main()
