from datetime import datetime
import threading
import time
import os

try:
    import requests
except ImportError:
    requests = None

from local_services.local_db import Accounts, Sessions


PING_URL = "http://localhost:8501"

INACTIVE_SECONDS = 180
DELETE_UNUSED_SESSION_SECONDS = 300

# This matches the 60-second miner timer in ethan_coin/mine/mine.py.
MINER_SECONDS = 60


def normalize_id(value):
    if isinstance(value, dict) and "$oid" in value:
        return str(value["$oid"])
    return str(value)


def normalize_datetime(value):
    if isinstance(value, datetime):
        return value

    if isinstance(value, dict) and "$date" in value:
        value = value["$date"]

    if isinstance(value, str):
        value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt

    raise ValueError(f"Cannot convert value to datetime: {value!r}")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def safe_seconds_since(date_value):
    try:
        return (datetime.utcnow() - normalize_datetime(date_value)).total_seconds()
    except Exception:
        return 999999


def ping_local_app():
    if requests is None:
        print("requests is not installed, so ping is disabled.")
        return

    try:
        response = requests.get(PING_URL, timeout=5)
        print(response)
    except Exception as e:
        print(f"Ping failed: {e}")


def reset_omega_chat():
    Sessions.update_one(
        {"_id": "OMEGA_CHAT"},
        {"$set": {"history": [], "people": []}}
    )
    print("Omega Reseted")


def reset_accounts():
    for account in Accounts.find():
        Accounts.update_one(
            {"_id": account["_id"]},
            {"$set": {"inbox": [], "status": "Peasent"}}
        )

    print("All account inboxes cleared and statuses reset to Peasent.")


def clean_miners_once():
    """
    External miner cleanup.

    mine.py starts a miner by setting:
      miner["status"] = "Mining"
      miner["time"] = datetime.utcnow()

    The mine.py page loop normally sets the miner back to Sleeping after 60 seconds.
    But if the user closes the tab or leaves the page, that loop stops running.
    This function fixes stuck miners globally by scanning every account.

    Important:
      This does NOT award extra EthanCoin.
      It only prevents miners from staying stuck as Mining forever.
    """
    total_reset = 0

    for account in list(Accounts.find()):
        miners = list(account.get("miners", []))
        changed = False

        for miner in miners:
            if miner.get("status") == "Mining":
                seconds_running = safe_seconds_since(miner.get("time"))

                if seconds_running >= MINER_SECONDS:
                    miner["status"] = "Sleeping"
                    changed = True
                    total_reset += 1
                    print(
                        f"Put miner {miner.get('_id')} ({miner.get('name')}) "
                        f"back to Sleeping for account {account.get('username')}"
                    )

        if changed:
            Accounts.update_one(
                {"_id": account["_id"]},
                {"$set": {"miners": miners}}
            )

    if total_reset == 0:
        print("No stuck miners found.")
    else:
        print(f"Reset {total_reset} miner(s).")


def clean_sessions_once():
    ping_local_app()

    for session in list(Sessions.find()):
        people = session.get("people", [])
        history = session.get("history", [])

        active_ids = [normalize_id(person.get("_id")) for person in people]

        for message in reversed(history):
            # Some old chat code used message["_id"] as the active/user id;
            # newer messages usually use message["userid"].
            message_user_id = normalize_id(message.get("userid", message.get("_id")))

            if message_user_id in active_ids:
                dif = safe_seconds_since(message.get("date"))

                if dif > INACTIVE_SECONDS:
                    for person in people:
                        if normalize_id(person.get("_id")) == message_user_id:
                            person_date = person.get("date")
                            message_date = message.get("date")

                            try:
                                if normalize_datetime(person_date) > normalize_datetime(message_date):
                                    break
                            except Exception:
                                pass

                            Sessions.update_one(
                                {"_id": session["_id"]},
                                {"$pull": {"people": person}}
                            )
                            print(f"Removed inactive person from session {session['_id']}")
                            break

                active_ids.remove(message_user_id)

        if active_ids != []:
            for person_id in active_ids:
                for person in people:
                    if normalize_id(person.get("_id")) == person_id:
                        dif = safe_seconds_since(person.get("date"))

                        if dif > INACTIVE_SECONDS:
                            Sessions.update_one(
                                {"_id": session["_id"]},
                                {"$pull": {"people": person}}
                            )
                            print(f"Removed stale person from session {session['_id']}")
                            break

        if session["_id"] != "OMEGA_CHAT":
            if len(history) == 0:
                latest_use = session.get("date")
            else:
                latest_use = history[-1].get("date")

            dif = safe_seconds_since(latest_use)

            if dif > DELETE_UNUSED_SESSION_SECONDS:
                Sessions.delete_one({"_id": session["_id"]})
                print(f"Deleted unused session {session['_id']}")


def clean_everything_once():
    clean_sessions_once()
    clean_miners_once()


def every_two():
    while True:
        time.sleep(2)
        clean_everything_once()


def main():
    loop_on = False

    while True:
        while True:
            clear_screen()
            print("1. Reset Omega Chat")
            print("2. Ping local app")
            print("3. Reset all account inboxes/statuses")
            print("4. Clean sessions once")
            print("5. Clean miners once")
            print("6. Clean sessions + miners once")
            print("type: STARTLOOP, to start loop checking")

            if loop_on:
                print("Loop is currently on")

            print()

            choices = ["1", "2", "3", "4", "5", "6", "STARTLOOP"]
            c = input("Enter: ").strip()

            clear_screen()

            if c in choices:
                break

            print("Invalid")
            time.sleep(1)

        if c == "1":
            reset_omega_chat()
            time.sleep(1)

        elif c == "2":
            ping_local_app()
            time.sleep(2)

        elif c == "3":
            confirm = input("Type RESET to clear every account inbox and set status to Peasent: ")
            if confirm == "RESET":
                reset_accounts()
            else:
                print("Cancelled.")
            time.sleep(2)

        elif c == "4":
            clean_sessions_once()
            print("Session clean complete.")
            time.sleep(2)

        elif c == "5":
            clean_miners_once()
            print("Miner clean complete.")
            time.sleep(2)

        elif c == "6":
            clean_everything_once()
            print("Session + miner clean complete.")
            time.sleep(2)

        elif c == "STARTLOOP":
            if loop_on:
                print("Loop already running")
                time.sleep(1)
                continue

            t = threading.Thread(target=every_two, daemon=True)
            t.start()
            loop_on = True
            print("Loop now ON")
            time.sleep(1)


if __name__ == "__main__":
    main()
