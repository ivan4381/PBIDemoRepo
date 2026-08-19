#!/usr/bin/env python3
"""
Script untuk cek status refresh report di Fabric Workspace
Cari workspace "self analytics production" dan report "DP LPG"
"""

import json
import requests
from azure.identity import DeviceCodeCredential
from datetime import datetime, timezone

# Konfigurasi
FABRIC_API_ENDPOINT = "https://api.fabric.microsoft.com/v1"
SCOPE = "https://api.fabric.microsoft.com/.default"

def get_access_token():
    """Dapatkan access token menggunakan Device Code Flow"""
    print("\n🔐 Login dengan Device Code Flow...")
    print("Silakan buka link yang akan ditampilkan dan ikuti instruksi di browser Anda.\n")

    credential = DeviceCodeCredential()
    token = credential.get_token(SCOPE)
    return token.token

def list_workspaces(access_token):
    """List semua workspace"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        print("📁 Mengambil daftar workspace...")
        response = requests.get(
            f"{FABRIC_API_ENDPOINT}/workspaces",
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("value", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing workspaces: {e}")
        return []

def find_workspace(workspaces, workspace_name):
    """Cari workspace berdasarkan nama"""
    for ws in workspaces:
        if ws.get("displayName", "").lower() == workspace_name.lower():
            return ws
    return None

def list_workspace_items(access_token, workspace_id):
    """List semua items dalam workspace"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        print(f"📋 Mengambil daftar items di workspace...")
        response = requests.get(
            f"{FABRIC_API_ENDPOINT}/workspaces/{workspace_id}/items",
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("value", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing items: {e}")
        return []

def get_item_refresh_schedule(access_token, workspace_id, item_id):
    """Get refresh schedule untuk item"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FABRIC_API_ENDPOINT}/workspaces/{workspace_id}/items/{item_id}/refreshSchedules",
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("value", [])
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error getting refresh schedule: {e}")
        return []

def get_item_refresh_history(access_token, workspace_id, item_id):
    """Get refresh history untuk item"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{FABRIC_API_ENDPOINT}/workspaces/{workspace_id}/items/{item_id}/refreshes",
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("value", [])
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error getting refresh history: {e}")
        return []

def check_refresh_today(refresh_history):
    """Cek apakah sudah ada refresh hari ini"""
    if not refresh_history:
        return False, None

    today = datetime.now(timezone.utc).date()

    for refresh in refresh_history:
        refresh_time_str = refresh.get("endTime") or refresh.get("startTime")
        if refresh_time_str:
            try:
                # Parse ISO format datetime
                refresh_time = datetime.fromisoformat(refresh_time_str.replace('Z', '+00:00'))
                if refresh_time.date() == today:
                    status = refresh.get("status", "Unknown")
                    return True, {"time": refresh_time_str, "status": status}
            except:
                pass

    return False, None

def display_report_info(report, refresh_history, refresh_schedules):
    """Tampilkan informasi report secara rapi"""
    print("\n" + "=" * 80)
    print(f"📊 REPORT: {report.get('displayName')}")
    print("=" * 80)
    print(f"   ID: {report.get('id')}")
    print(f"   Type: {report.get('type')}")
    print(f"   Description: {report.get('description', 'N/A')}")

    # Cek refresh hari ini
    has_refreshed_today, refresh_info = check_refresh_today(refresh_history)

    print(f"\n🔄 STATUS REFRESH:")
    if has_refreshed_today:
        print(f"   ✅ SUDAH REFRESH HARI INI")
        print(f"   Waktu: {refresh_info['time']}")
        print(f"   Status: {refresh_info['status']}")
    else:
        print(f"   ❌ BELUM REFRESH HARI INI")

    # Tampilkan refresh history terbaru
    if refresh_history:
        print(f"\n📅 REFRESH HISTORY (5 terakhir):")
        for i, refresh in enumerate(refresh_history[:5], 1):
            refresh_time = refresh.get("endTime") or refresh.get("startTime")
            status = refresh.get("status", "Unknown")
            print(f"   {i}. {refresh_time} - {status}")

    # Tampilkan refresh schedule
    if refresh_schedules:
        print(f"\n⏰ REFRESH SCHEDULE:")
        for schedule in refresh_schedules:
            print(f"   Frequency: {schedule.get('frequency', 'N/A')}")
            if 'time' in schedule:
                print(f"   Time: {schedule.get('time')}")
    else:
        print(f"\n⏰ REFRESH SCHEDULE: Tidak ada jadwal refresh")

    print("=" * 80)

def main():
    try:
        # Step 1: Get access token
        access_token = get_access_token()
        print("✅ Login berhasil!")

        # Step 2: List all workspaces
        workspaces = list_workspaces(access_token)
        if not workspaces:
            print("❌ Tidak ada workspace ditemukan")
            return

        # Step 3: Find target workspace
        target_workspace_name = "self analytics production"
        workspace = find_workspace(workspaces, target_workspace_name)

        if not workspace:
            print(f"❌ Workspace '{target_workspace_name}' tidak ditemukan")
            print(f"\n📁 Workspace yang tersedia:")
            for ws in workspaces:
                print(f"   - {ws.get('displayName')}")
            return

        workspace_id = workspace.get("id")
        print(f"\n✅ Workspace ditemukan: {workspace.get('displayName')}")
        print(f"   ID: {workspace_id}")

        # Step 4: List items in workspace
        items = list_workspace_items(access_token, workspace_id)
        if not items:
            print(f"❌ Tidak ada items di workspace ini")
            return

        # Step 5: Find target report
        target_report_name = "DP LPG"
        report = None

        for item in items:
            if target_report_name.lower() in item.get("displayName", "").lower():
                report = item
                break

        if not report:
            print(f"❌ Report '{target_report_name}' tidak ditemukan")
            print(f"\n📋 Items yang tersedia:")
            for item in items:
                print(f"   - {item.get('displayName')} ({item.get('type')})")
            return

        print(f"\n✅ Report ditemukan: {report.get('displayName')}")

        # Step 6: Get refresh information
        refresh_schedules = get_item_refresh_schedule(access_token, workspace_id, report.get("id"))
        refresh_history = get_item_refresh_history(access_token, workspace_id, report.get("id"))

        # Step 7: Display info
        display_report_info(report, refresh_history, refresh_schedules)

        # Save hasil ke file JSON
        result = {
            "workspace": {
                "name": workspace.get("displayName"),
                "id": workspace.get("id")
            },
            "report": {
                "name": report.get("displayName"),
                "id": report.get("id"),
                "type": report.get("type")
            },
            "refresh_info": {
                "has_refreshed_today": check_refresh_today(refresh_history)[0],
                "schedules": refresh_schedules,
                "history": refresh_history[:10]  # Save 10 latest
            }
        }

        with open("fabric_report_refresh_status.json", "w") as f:
            json.dump(result, f, indent=2)

        print(f"\n💾 Hasil detail disimpan ke: fabric_report_refresh_status.json")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
