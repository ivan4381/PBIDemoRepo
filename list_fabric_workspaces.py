#!/usr/bin/env python3
"""
Script untuk list semua Fabric Workspace yang accessible
Menggunakan interactive login (browser-based authentication)
"""

import json
import requests
from azure.identity import InteractiveBrowserCredential

# Konfigurasi
AUTHORITY_URL = "https://login.microsoftonline.com"
FABRIC_API_ENDPOINT = "https://api.fabric.microsoft.com/v1"
SCOPE = "https://api.fabric.microsoft.com/.default"

def get_access_token():
    """Dapatkan access token menggunakan interactive browser login"""
    print("🔐 Membuka browser untuk login interaktif...")
    credential = InteractiveBrowserCredential()
    token = credential.get_token(SCOPE)
    return token.token

def list_workspaces(access_token):
    """List semua workspace yang accessible"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        print("\n📁 Mengambil daftar workspace...")
        response = requests.get(
            f"{FABRIC_API_ENDPOINT}/workspaces",
            headers=headers
        )
        response.raise_for_status()

        workspaces = response.json()
        return workspaces
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def display_workspaces(workspaces):
    """Tampilkan workspace dalam format yang rapi"""
    if not workspaces or "value" not in workspaces:
        print("⚠️ Tidak ada workspace ditemukan atau response tidak valid")
        return

    workspace_list = workspaces.get("value", [])

    if not workspace_list:
        print("⚠️ Tidak ada workspace yang accessible")
        return

    print(f"\n✅ Ditemukan {len(workspace_list)} workspace:\n")
    print("=" * 80)

    for i, workspace in enumerate(workspace_list, 1):
        workspace_id = workspace.get("id", "N/A")
        workspace_name = workspace.get("displayName", "N/A")
        workspace_type = workspace.get("type", "N/A")

        print(f"\n{i}. {workspace_name}")
        print(f"   ID: {workspace_id}")
        print(f"   Type: {workspace_type}")

    print("\n" + "=" * 80)

def main():
    try:
        # Step 1: Get access token
        access_token = get_access_token()
        print("✅ Login berhasil!")

        # Step 2: List workspaces
        workspaces = list_workspaces(access_token)

        # Step 3: Display results
        if workspaces:
            display_workspaces(workspaces)

            # Save hasil ke file JSON
            with open("fabric_workspaces.json", "w") as f:
                json.dump(workspaces, f, indent=2)
            print("\n💾 Hasil disimpan ke: fabric_workspaces.json")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
