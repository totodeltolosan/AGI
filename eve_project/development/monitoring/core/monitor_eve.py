#!/usr/bin/env python3
import requests
import json
import time
import sys

def monitor_eve_status(task_id):
    """TODO: Add docstring."""
    print(f"🎯 Monitoring EVE GENESIS Task: {task_id}")
    print("=" * 60)

    while True:
        try:
            response = requests.get(f"http://127.0.0.1:8000/status/{task_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                details = data.get('details', 'No details')

                print(f"\n⏰ {time.strftime('%H:%M:%S')} - Status: {status.upper()}")
                print(f"📝 Details: {details[:200]}...")

                if status in ['completed', 'failed']:
                    print(f"\n🎉 Final Status: {status.upper()}")
                    print(f"📋 Final Details: {details}")
                    break

            else:
                print(f"❌ Error: {response.status_code}")

        except Exception as e:
            print(f"🔄 Connection error: {e}")

        time.sleep(10)  # Vérifier toutes les 10 secondes

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
    else:
        task_id = "0e56008a-c4dc-4e1b-ac18-9bf1a4f688ba"  # Votre task_id actuel

    monitor_eve_status(task_id)