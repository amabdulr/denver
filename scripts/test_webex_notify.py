#!/usr/bin/env python3
"""
Quick test: send a Webex message via the Webex REST API.

Usage:
    python scripts/test_webex_notify.py

Before running, add these to Denver2/.env (or env/.env):
    WEBEX_BOT_TOKEN=<your-bot-token>
    WEBEX_ROOM_ID=<target-room-id>

To get these:
  1. Create a bot at https://developer.webex.com/my-apps/new/bot
  2. Add the bot to a Webex space
  3. Get the room ID:
       curl -s -H "Authorization: Bearer <BOT_TOKEN>" \
         https://webexapis.com/v1/rooms | python3 -m json.tool
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv

# ── Load .env ──────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

for env_candidate in [PROJECT_DIR / ".env", PROJECT_DIR / "env" / ".env"]:
    if env_candidate.exists():
        load_dotenv(env_candidate)
        break

WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "")
WEBEX_ROOM_ID = os.getenv("WEBEX_ROOM_ID", "")
WEBEX_API = "https://webexapis.com/v1/messages"


# ── Core notify function (reusable) ───────────────────────────
def notify_webex(message: str, *, room_id: str = "", token: str = "") -> dict:
    """Post a Markdown message to a Webex space. Returns the API response dict."""
    token = token or WEBEX_BOT_TOKEN
    room_id = room_id or WEBEX_ROOM_ID

    if not token:
        return {"ok": False, "error": "WEBEX_BOT_TOKEN not set"}
    if not room_id:
        return {"ok": False, "error": "WEBEX_ROOM_ID not set"}

    resp = requests.post(
        WEBEX_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"roomId": room_id, "markdown": message},
        timeout=15,
    )

    if resp.status_code in (200, 201):
        return {"ok": True, "id": resp.json().get("id", ""), "status": resp.status_code}
    else:
        return {"ok": False, "status": resp.status_code, "error": resp.text[:300]}


# ── Helpers: list rooms (useful for discovering room IDs) ──────
def list_rooms(token: str = "") -> list:
    """Return a list of rooms the bot belongs to."""
    token = token or WEBEX_BOT_TOKEN
    if not token:
        print("ERROR: WEBEX_BOT_TOKEN not set")
        return []
    resp = requests.get(
        "https://webexapis.com/v1/rooms",
        headers={"Authorization": f"Bearer {token}"},
        params={"max": 50, "sortBy": "lastactivity"},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"ERROR listing rooms: {resp.status_code} — {resp.text[:200]}")
        return []
    return resp.json().get("items", [])


# ── CLI ────────────────────────────────────────────────────────
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test Webex notifications")
    parser.add_argument("--list-rooms", action="store_true", help="List rooms the bot belongs to (use to find WEBEX_ROOM_ID)")
    parser.add_argument("--message", "-m", type=str, default="", help="Custom message to send")
    args = parser.parse_args()

    # ── List rooms mode ──
    if args.list_rooms:
        if not WEBEX_BOT_TOKEN:
            print("Set WEBEX_BOT_TOKEN in .env first.")
            sys.exit(1)
        rooms = list_rooms()
        if not rooms:
            print("No rooms found. Add the bot to a Webex space first.")
            sys.exit(1)
        print(f"\n{'Title':<45} {'Room ID'}")
        print("─" * 100)
        for r in rooms:
            print(f"{r['title'][:44]:<45} {r['id']}")
        print(f"\nCopy the room ID you want into .env as WEBEX_ROOM_ID")
        return

    # ── Send test message ──
    print("Webex Notification Test")
    print("═" * 40)

    if not WEBEX_BOT_TOKEN:
        print("✗ WEBEX_BOT_TOKEN not set in .env")
        print("  → Create a bot at https://developer.webex.com/my-apps/new/bot")
        sys.exit(1)
    print("✓ WEBEX_BOT_TOKEN found")

    if not WEBEX_ROOM_ID:
        print("✗ WEBEX_ROOM_ID not set in .env")
        print("  → Run: python scripts/test_webex_notify.py --list-rooms")
        sys.exit(1)
    print(f"✓ WEBEX_ROOM_ID found ({WEBEX_ROOM_ID[:12]}…)")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = args.message or (
        f"**Hello from CT Factory!**\n\n"
        f"This is a test notification. Your Webex integration is working.\n\n"
        f"- Time: `{now}`\n"
        f"- Host: `{os.uname().nodename}`\n"
        f"- Bot is online and ready\n"
        f"- Can notify on: bulk convert, bulk review, kgraph runs, downloads, etc.\n\n"
        f"_Sent automatically via CT Factory_"
    )

    print(f"\nSending message to Webex…")
    result = notify_webex(msg)

    if result.get("ok"):
        print(f"✓ Message sent! (HTTP {result['status']})")
        print(f"  Message ID: {result['id'][:20]}…")
    else:
        print(f"✗ Failed: {result.get('error', 'unknown error')}")
        if result.get("status") == 401:
            print("  → Token is invalid or expired. Regenerate at developer.webex.com")
        elif result.get("status") == 404:
            print("  → Room not found. Check WEBEX_ROOM_ID or run --list-rooms")
        sys.exit(1)

    print("\nDone. The notify_webex() function is ready to import into any script.")


if __name__ == "__main__":
    main()
