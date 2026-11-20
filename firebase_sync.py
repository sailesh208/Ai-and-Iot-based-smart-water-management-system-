#!/usr/bin/env python3
"""
AquaNest Firebase Cloud Firestore Utility & CLI
Provides tools to test connection, view Firestore collections, seed initial schemas,
and synchronize data with Google Cloud Firestore.
"""

import sys
import os
import argparse
import json

import sys
import os
import argparse
import json
import warnings

# Suppress python version deprecation warnings from google cloud packages
warnings.filterwarnings("ignore")

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure dashboard directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "dashboard")))

from services.firebase_service import get_firebase_service


def print_banner():
    print("=" * 65)
    print(" AQUANEST - FIREBASE CLOUD FIRESTORE INTEGRATION UTILITY")
    print("=" * 65)



def check_status():
    fb = get_firebase_service()
    stats = fb.test_connection()

    print("\n🔍 Firebase Connection Status:")
    print(f"  • Connected to Cloud:  {'✅ YES' if stats['is_connected'] else '🟡 LOCAL PERSISTENCE / SIMULATION'}")
    print(f"  • Operating Mode:      {stats['mode']}")
    print(f"  • Firebase Project ID: {stats['project_id']}")
    print(f"  • Credentials Source:  {stats['credentials_path']}")
    print(f"  • Python SDK Ready:    {'✅ Available' if stats['sdk_available'] else '❌ Not installed'}")
    print(f"  • Response Latency:    {stats['latency_ms']} ms")
    if stats.get("error"):
        print(f"  • Diagnostic Note:     {stats['error']}")

    print("\n📊 Firestore Collections & Documents:")
    print("  " + "-" * 40)
    print(f"  {'Collection Name':<20} | {'Document Count':<15}")
    print("  " + "-" * 40)
    for col, count in stats["collections"].items():
        print(f"  {col:<20} | {count:<15}")
    print("  " + "-" * 40)
    total_docs = sum(stats["collections"].values())
    print(f"  {'TOTAL DOCUMENTS':<20} | {total_docs:<15}\n")


def seed_database():
    fb = get_firebase_service()
    print("\n🚀 Seeding AquaNest Collections to Firebase Firestore...")
    results = fb.seed_initial_collections()
    print("✅ Seeding completed successfully!")
    for col, count in results.items():
        print(f"  • {col}: {count} documents committed.")
    print()


def connect_key(key_path: str, project_id: str = None):
    fb = get_firebase_service()
    print(f"\n🔑 Connecting with service account key: {key_path}...")
    success, msg = fb.connect_with_credentials_file(key_path, project_id)
    if success:
        print(f"✅ {msg}")
        check_status()
    else:
        print(f"❌ {msg}")


def main():
    parser = argparse.ArgumentParser(description="AquaNest Firebase Cloud Firestore Utility")
    parser.add_argument("--status", action="store_true", help="Check Firebase Firestore connection status and collection stats")
    parser.add_argument("--seed", action="store_true", help="Seed standard AquaNest collections and demo telemetry")
    parser.add_argument("--connect", type=str, help="Path to Firebase Service Account JSON key file")
    parser.add_argument("--project", type=str, help="Firebase Project ID")

    args = parser.parse_args()
    print_banner()

    if args.connect:
        connect_key(args.connect, args.project)
    elif args.seed:
        seed_database()
        check_status()
    else:
        check_status()


if __name__ == "__main__":
    main()
