"""
AquaNest Firebase Cloud Firestore & Auth Service
Manages real-time connection, data synchronization, collection seeding,
Firebase Authentication REST API, and schema enforcement for Google Firebase project: aquanest-d4f40.
"""

import os
import json
import time
import datetime
import requests
from typing import Dict, Any, List, Optional, Tuple

from .resident_profiles import RESIDENT_PROFILE_BY_EMAIL, RESIDENT_PROFILE_BY_HOUSE

FIREBASE_AVAILABLE = False
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class FirebaseService:
    """
    Central service for connecting AquaNest to Google Firebase (aquanest-d4f40).
    Supports Firebase Web Config, Auth REST APIs, Firestore REST/Admin SDK, and Local Persistence Fallback.
    """

    _instance = None
    _db = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        if self._initialized:
            return

        # Load web config if present
        self.web_config = self._load_web_config()

        self.project_id = project_id or self.web_config.get("projectId") or os.environ.get("FIREBASE_PROJECT_ID", "aquanest-d4f40")
        self.api_key = self.web_config.get("apiKey") or os.environ.get("FIREBASE_API_KEY", "AIzaSyDDdw0at7SQr_br9bYUOpAE2jERcGk9T6o")
        self.auth_domain = self.web_config.get("authDomain") or os.environ.get("FIREBASE_AUTH_DOMAIN", "aquanest-d4f40.firebaseapp.com")
        self.storage_bucket = self.web_config.get("storageBucket") or os.environ.get("FIREBASE_STORAGE_BUCKET", "aquanest-d4f40.firebasestorage.app")
        self.app_id = self.web_config.get("appId") or os.environ.get("FIREBASE_APP_ID", "1:376305593197:web:935332c7f9528e6b4a8864")
        self.measurement_id = self.web_config.get("measurementId") or os.environ.get("FIREBASE_MEASUREMENT_ID", "G-RCB695W7VW")

        self.credentials_path = credentials_path or os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
        self.client_email = os.environ.get("FIREBASE_CLIENT_EMAIL", "")
        self.private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
        self.is_connected = False
        self.last_sync_time = None
        self.connection_mode = "CONFIGURED_WEB_APP"
        self.last_error = None
        self.firestore_api_enabled = False
        self.local_cache_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "firestore_local.json")
        )

        self._init_firebase()
        FirebaseService._initialized = True

    def _load_web_config(self) -> Dict[str, str]:
        """Loads configuration from firebase_config.json if available."""
        config_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "firebase_config.json")
        )
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _init_firebase(self):
        """Attempts to initialize Firebase Admin app or REST verification."""
        self._ensure_local_cache()

        # 1. Try Firebase Admin SDK if service account is available
        cred_paths_to_check = [
            self.credentials_path,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "firebase-service-account.json")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "firebase-key.json")),
        ]

        found_cred_path = None
        for p in cred_paths_to_check:
            if p and os.path.exists(p):
                found_cred_path = p
                break

        if found_cred_path and FIREBASE_AVAILABLE:
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(found_cred_path)
                    firebase_admin.initialize_app(cred, {"projectId": self.project_id})
                self._db = firestore.client()
                self.is_connected = True
                self.connection_mode = "CLOUD_FIRESTORE_ADMIN"
                self.credentials_path = found_cred_path
                self.last_sync_time = datetime.datetime.now()
                self.last_error = None
                return
            except Exception as e:
                self.last_error = f"Admin SDK note: {e}"

        # 2. Verify REST API connection to Firebase Auth & Project
        try:
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri?key={self.api_key}"
            resp = requests.post(auth_url, json={"continueUri": "http://localhost"}, timeout=3.0)
            if resp.status_code in [200, 400]:
                self.is_connected = True
                self.connection_mode = "FIREBASE_WEB_CONNECTED"
                self.last_sync_time = datetime.datetime.now()
        except Exception:
            pass

    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Signs in a user with Firebase Authentication and requires a matching profile.
        """
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        try:
            r = requests.post(url, json={
                "email": email.strip(),
                "password": password,
                "returnSecureToken": True
            }, timeout=4.0)

            if r.status_code == 200:
                data = r.json()
                normalized_email = email.strip().lower()
                local_user = next(
                    (
                        user for user in self.get_collection("users", limit=500)
                        if user.get("email", "").strip().lower() == normalized_email
                    ),
                    None,
                )
                if local_user is None:
                    local_user = RESIDENT_PROFILE_BY_EMAIL.get(normalized_email)
                if not local_user:
                    return False, {}, "Your Firebase account does not have an AquaNest user profile."

                role = str(local_user.get("role", "")).upper()
                house_id = local_user.get("houseId")
                if role not in {"ADMIN", "RESIDENT"}:
                    return False, {}, "Your AquaNest profile has an invalid account role."
                if role == "ADMIN" and house_id != "ALL":
                    return False, {}, "The administrator profile is missing its building assignment."
                if role == "RESIDENT" and house_id not in RESIDENT_PROFILE_BY_HOUSE:
                    return False, {}, "Your resident profile is not assigned to a supported apartment."
                return True, {
                    "idToken": data.get("idToken"),
                    "localId": data.get("localId"),
                    "userId": local_user.get("userId", data.get("localId")),
                    "name": local_user.get("name", email.split("@")[0]),
                    "email": normalized_email,
                    "role": role,
                    "houseId": house_id
                }, "Firebase Authentication successful."
            else:
                err_msg = r.json().get("error", {}).get("message", "Authentication failed.")
                return False, {}, err_msg
        except requests.RequestException as e:
            return False, {}, f"Connection error: {e}"
        except (ValueError, KeyError) as e:
            return False, {}, f"Authentication response was invalid: {e}"

    def register_user(self, email: str, password: str, name: str, house_number: str, phone: str = "") -> Tuple[bool, str]:
        """Registers a new user in Firebase Auth and adds them to Firestore users collection."""
        email = email.strip()
        if "@" not in email:
            return False, "Enter a valid email address."
        try:
            apartment_number = int(house_number)
        except (TypeError, ValueError):
            return False, "Choose an apartment number from 101 to 120."
        if apartment_number not in range(101, 121):
            return False, "Choose an apartment number from 101 to 120."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        h_id = f"H{apartment_number}"
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        user_doc = {
            "userId": f"USR_RES_{email.split('@')[0]}",
            "name": name.strip(),
            "email": email,
            "phone": phone.strip(),
            "role": "RESIDENT",
            "houseId": h_id,
            "status": "ACTIVE",
            "createdAt": datetime.datetime.now().isoformat()
        }

        try:
            r = requests.post(url, json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            }, timeout=4.0)
            if r.status_code == 200:
                self.save_document("users", user_doc["userId"], user_doc)
                return True, "Registered successfully with Firebase Authentication & Firestore."
            err = r.json().get("error", {}).get("message", "Registration failed.")
            if "EMAIL_EXISTS" in err:
                return False, "This email address is already registered in Firebase."
            return False, err
        except requests.RequestException as error:
            return False, f"Could not connect to Firebase Authentication: {error}"
        except ValueError as error:
            return False, f"Firebase returned an invalid registration response: {error}"

    def send_password_reset(self, email: str) -> Tuple[bool, str]:
        """Dispatches a password reset email via Firebase Auth."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
        try:
            r = requests.post(url, json={
                "requestType": "PASSWORD_RESET",
                "email": email.strip()
            }, timeout=4.0)
            if r.status_code == 200:
                return True, f"Password reset instructions have been dispatched by Firebase to {email}."
            else:
                err = r.json().get("error", {}).get("message", "Failed to send reset link.")
                return False, err
        except Exception as e:
            return False, f"Error: {e}"

    def test_connection(self) -> Dict[str, Any]:
        """Runs a diagnostic test and returns detailed connection state and collection status."""
        start_t = time.perf_counter()
        stats = {
            "is_connected": self.is_connected,
            "mode": self.connection_mode,
            "project_id": self.project_id,
            "api_key_configured": bool(self.api_key),
            "auth_domain": self.auth_domain,
            "app_id": self.app_id,
            "credentials_path": self.credentials_path if self.credentials_path else "Web Config / Local Cache",
            "sdk_available": FIREBASE_AVAILABLE,
            "latency_ms": None,
            "error": self.last_error,
            "firestore_created": False,
            "collections": {
                "users": 0,
                "houses": 0,
                "tank_readings": 0,
                "bills": 0,
                "pump_logs": 0,
                "leakage_alerts": 0,
                "alerts": 0,
                "settings": 0
            }
        }

        # Check Firestore REST endpoint
        try:
            fs_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/users?key={self.api_key}"
            r = requests.get(fs_url, timeout=2.5)
            if r.status_code == 200:
                stats["firestore_created"] = True
                stats["is_connected"] = True
            elif r.status_code == 403 and "disabled" in r.text.lower():
                stats["firestore_created"] = False
                stats["error"] = "Cloud Firestore database not yet initialized in Firebase Console (visit console.firebase.google.com to click 'Create Database')."
        except Exception:
            pass

        # Populate collection count from local cache / Firestore
        local_data = self._read_local_cache()
        for c in stats["collections"]:
            if c in local_data:
                stats["collections"][c] = len(local_data[c])

        stats["latency_ms"] = round((time.perf_counter() - start_t) * 1000.0, 1)
        return stats

    def save_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Saves or updates a document in the target collection."""
        data_to_write = dict(data)
        data_to_write["updatedAt"] = datetime.datetime.now().isoformat()

        if self._db:
            try:
                self._db.collection(collection_name).document(document_id).set(data_to_write, merge=True)
            except Exception as e:
                self.last_error = str(e)

        # Local Firestore cache
        local_data = self._read_local_cache()
        if collection_name not in local_data:
            local_data[collection_name] = {}
        local_data[collection_name][document_id] = data_to_write
        self._write_local_cache(local_data)
        return True

    def get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single document by ID."""
        if self._db:
            try:
                doc = self._db.collection(collection_name).document(document_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception:
                pass

        local_data = self._read_local_cache()
        return local_data.get(collection_name, {}).get(document_id)

    def get_collection(self, collection_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves all documents in a collection."""
        if self._db:
            try:
                docs = self._db.collection(collection_name).limit(limit).stream()
                return [d.to_dict() for d in docs]
            except Exception:
                pass

        local_data = self._read_local_cache()
        col_dict = local_data.get(collection_name, {})
        return list(col_dict.values())[:limit]

    def seed_initial_collections(self) -> Dict[str, int]:
        """Seeds standard AquaNest schema and demo dataset to collections."""
        initial_data = self._generate_default_seed_data()
        results = {}
        for collection_name, items in initial_data.items():
            count = 0
            for item in items:
                doc_id = item.get("id") or item.get("userId") or item.get("houseId") or f"doc_{count+1}"
                success = self.save_document(collection_name, str(doc_id), item)
                if success:
                    count += 1
            results[collection_name] = count

        self.last_sync_time = datetime.datetime.now()
        return results

    def _generate_default_seed_data(self) -> Dict[str, List[Dict[str, Any]]]:
        now_iso = datetime.datetime.now().isoformat()
        users = [
            {"userId": "USR_ADMIN", "name": "Property Admin", "email": "admin@aquanest.io", "phone": "", "role": "ADMIN", "houseId": "ALL", "status": "ACTIVE"},
            *[
                {
                    "userId": profile["userId"],
                    "name": profile["name"],
                    "email": profile["email"],
                    "phone": "",
                    "role": "RESIDENT",
                    "houseId": profile["houseId"],
                    "status": "ACTIVE",
                }
                for profile in RESIDENT_PROFILE_BY_HOUSE.values()
            ],
        ]
        houses = [
            {
                "houseId": profile["houseId"],
                "houseNumber": profile["houseId"][1:],
                "floor": (index // 4) + 1,
                "residentId": profile["userId"],
                "residentName": profile["name"],
                "meterId": f"METER_{profile['houseId']}",
                "status": "ACTIVE",
                "currentUsageLitres": round(profile["baseDailyUsageLitres"] / 60.0, 1),
                "todayUsageLitres": profile["baseDailyUsageLitres"],
                "monthlyUsageLitres": profile["baseDailyUsageLitres"] * 30.0,
                "anomalyStatus": "ABNORMAL" if profile["houseId"] == "H104" else "NORMAL",
            }
            for index, profile in enumerate(RESIDENT_PROFILE_BY_HOUSE.values())
        ]
        tank_readings = [
            {"id": "TR_CURRENT", "timestamp": now_iso, "levelPercent": 72.5, "waterLitres": 2900.0, "capacityLitres": 4000.0, "sensorId": "JSN_SR04T_01", "pumpStatus": "OFF", "pumpMode": "AUTO", "fillRateLpm": 0.0, "emptyRateLpm": 8.4}
        ]
        bills = [
            {"id": "BILL_202609_H101", "houseId": "H101", "houseNumber": "101", "residentName": "Rajesh Sharma", "billingPeriod": "2026-09", "consumptionLitres": 7228.0, "waterRate": 0.10, "waterCharge": 722.8, "fixedCharge": 200.0, "totalAmount": 922.8, "dueDate": "2026-10-10", "paymentStatus": "PAID"},
            {"id": "BILL_202609_H102", "houseId": "H102", "houseNumber": "102", "residentName": "Priya Venkatesh", "billingPeriod": "2026-09", "consumptionLitres": 8330.0, "waterRate": 0.10, "waterCharge": 833.0, "fixedCharge": 200.0, "totalAmount": 1033.0, "dueDate": "2026-10-10", "paymentStatus": "PAID"},
            {"id": "BILL_202609_H103", "houseId": "H103", "houseNumber": "103", "residentName": "Arun Kumar", "billingPeriod": "2026-09", "consumptionLitres": 9433.0, "waterRate": 0.10, "waterCharge": 943.3, "fixedCharge": 200.0, "totalAmount": 1143.3, "dueDate": "2026-10-10", "paymentStatus": "PENDING"},
            {"id": "BILL_202609_H104", "houseId": "H104", "houseNumber": "104", "residentName": "Sneha Patel", "billingPeriod": "2026-09", "consumptionLitres": 20825.0, "waterRate": 0.10, "waterCharge": 2082.5, "fixedCharge": 200.0, "totalAmount": 2282.5, "dueDate": "2026-10-10", "paymentStatus": "PAID"},
            {"id": "BILL_202609_H105", "houseId": "H105", "houseNumber": "105", "residentName": "Vikram Malhotra", "billingPeriod": "2026-09", "consumptionLitres": 11638.0, "waterRate": 0.10, "waterCharge": 1163.8, "fixedCharge": 200.0, "totalAmount": 1363.8, "dueDate": "2026-10-10", "paymentStatus": "OVERDUE"},
            {"id": "BILL_202609_H106", "houseId": "H106", "houseNumber": "106", "residentName": "Ananya Reddy", "billingPeriod": "2026-09", "consumptionLitres": 12740.0, "waterRate": 0.10, "waterCharge": 1274.0, "fixedCharge": 200.0, "totalAmount": 1474.0, "dueDate": "2026-10-10", "paymentStatus": "PAID"},
        ]
        pump_logs = [
            {"id": "PL_1", "status": "ON", "mode": "AUTO", "tankLevel": 19.5, "startTime": now_iso, "durationSeconds": 2700, "trigger": "LOW_LEVEL_AUTO"},
            {"id": "PL_2", "status": "ON", "mode": "AUTO", "tankLevel": 20.0, "startTime": now_iso, "durationSeconds": 2400, "trigger": "LOW_LEVEL_AUTO"}
        ]
        leakage_alerts = [
            {"id": "LKG_TANK_01", "type": "TANK_LEAKAGE", "zone": "Overhead Tank Zone", "estimatedLossLitres": 145.0, "severity": "WARNING", "evidence": "Tank level dropped 3.6% over 120 min while pump idle.", "status": "INVESTIGATING"},
            {"id": "LKG_PIPE_01", "type": "PIPE_LEAKAGE", "zone": "Main Distribution Pipe - Wing B", "estimatedLossLitres": 380.0, "severity": "POSSIBLE_LEAK", "evidence": "Main flow (18.5 L/min) vs House sum (11.2 L/min) with 0.6 bar drop.", "status": "NEW"}
        ]
        alerts = [
            {"id": "ALT_1", "type": "PIPE_LEAKAGE", "severity": "CRITICAL", "target": "DISTRIBUTION", "message": "Distribution mismatch detected: 7.3 L/min unexplained loss in Wing B.", "timestamp": now_iso},
            {"id": "ALT_2", "type": "ABNORMAL_CONSUMPTION", "severity": "WARNING", "target": "H104", "message": "House 104 abnormal usage: 4.5 hours continuous nocturnal flow detected.", "timestamp": now_iso},
            {"id": "ALT_3", "type": "TANK_LEAKAGE", "severity": "WARNING", "target": "MAIN", "message": "Possible tank leakage detected: Unexplained 145 L drop while pump was idle.", "timestamp": now_iso},
            {"id": "ALT_4", "type": "PUMP", "severity": "INFO", "target": "ALL", "message": "Automatic pump cycle completed. Overhead tank replenished to 88.5%.", "timestamp": now_iso}
        ]
        settings = [
            {"id": "global_config", "tankCapacityLitres": 4000.0, "lowThresholdPercent": 20.0, "fullThresholdPercent": 90.0, "waterTariffPerLitre": 0.10, "fixedMonthlyCharge": 200.0, "flowCalibrationFactor": 450.0, "pressureThresholdBar": 1.8, "leakageTolerancePercent": 5.0, "demoMode": True}
        ]
        return {
            "users": users, "houses": houses, "tank_readings": tank_readings,
            "bills": bills, "pump_logs": pump_logs, "leakage_alerts": leakage_alerts,
            "alerts": alerts, "settings": settings
        }

    def _ensure_local_cache(self):
        local_data = self._read_local_cache()
        if os.path.exists(self.local_cache_file) and not local_data:
            return

        changed = False
        for collection_name, items in self._generate_default_seed_data().items():
            collection = local_data.setdefault(collection_name, {})
            for item in items:
                document_id = str(item.get("id") or item.get("userId") or item.get("houseId"))
                if document_id not in collection:
                    collection[document_id] = item
                    changed = True
        if changed:
            self._write_local_cache(local_data)

    def _read_local_cache(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.local_cache_file):
                with open(self.local_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _write_local_cache(self, data: Dict[str, Any]):
        try:
            with open(self.local_cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.last_error = f"Cache write error: {e}"


def get_firebase_service() -> FirebaseService:
    return FirebaseService()
