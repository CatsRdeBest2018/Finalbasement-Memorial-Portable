from pathlib import Path
from datetime import datetime
import json
import os
import shutil
import uuid


APP_DIR = Path(__file__).resolve().parent
DB_DIR = APP_DIR / "local_data" / "db"

ACCOUNTS_PATH = DB_DIR / "Accounts.json"
ETHANCOIN_PATH = DB_DIR / "EthanCoin.json"

TARGET_USERNAME = "ethan"
TARGET_COIN_COUNT = 40
TARGET_COIN_VALUE = 1.0


def normalize_id(value):
    if isinstance(value, dict) and "$oid" in value:
        return str(value["$oid"])
    return str(value)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def atomic_save_json(path, data):
    temp_path = path.with_suffix(path.suffix + f".tmp_{os.getpid()}_{uuid.uuid4().hex}")

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp_path, path)


def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = APP_DIR / "local_data" / f"db_backup_trim_ethan_coins_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ACCOUNTS_PATH, backup_dir / "Accounts.json")
    shutil.copy2(ETHANCOIN_PATH, backup_dir / "EthanCoin.json")

    return backup_dir


def main():
    print("FinalBasement EthanCoin trim script")
    print("----------------------------------")
    print(f"Target username: {TARGET_USERNAME}")
    print(f"Target final coin count: {TARGET_COIN_COUNT}")
    print(f"Target coin value: {TARGET_COIN_VALUE}")
    print()

    accounts = load_json(ACCOUNTS_PATH)
    coins = load_json(ETHANCOIN_PATH)

    target_account = None

    for account in accounts:
        if account.get("username") == TARGET_USERNAME:
            target_account = account
            break

    if target_account is None:
        raise RuntimeError(f'No account found with username "{TARGET_USERNAME}"')

    old_balance = target_account.get("balance", [])
    old_coin_ids = {
        normalize_id(coin_ref.get("_id"))
        for coin_ref in old_balance
        if isinstance(coin_ref, dict) and "_id" in coin_ref
    }

    print(f"Found account _id: {target_account.get('_id')}")
    print(f"Old balance entries: {len(old_balance)}")
    print(f"Unique old coin IDs referenced by account: {len(old_coin_ids)}")

    kept_coin_docs = []
    deleted_coin_docs = []

    for coin_doc in coins:
        current_id = normalize_id(coin_doc.get("currentId"))

        if current_id in old_coin_ids:
            deleted_coin_docs.append(coin_doc)
        else:
            kept_coin_docs.append(coin_doc)

    print(f"EthanCoin documents that will be removed: {len(deleted_coin_docs)}")
    print(f"EthanCoin documents not owned by this account and kept: {len(kept_coin_docs)}")
    print()

    confirm = input(
        f'Type DELETE to replace "{TARGET_USERNAME}" balance with '
        f'{TARGET_COIN_COUNT} coins worth {TARGET_COIN_VALUE} each: '
    )

    if confirm != "DELETE":
        print("Cancelled. No changes made.")
        return

    backup_dir = backup_files()
    print(f"Backup created at: {backup_dir}")

    new_balance = []
    new_coin_docs = []

    for _ in range(TARGET_COIN_COUNT):
        coin_doc_id = uuid.uuid4().hex
        coin_current_id = uuid.uuid4().hex

        new_coin_docs.append({
            "_id": coin_doc_id,
            "currentId": coin_current_id,
            "value": TARGET_COIN_VALUE
        })

        new_balance.append({
            "_id": coin_current_id
        })

    target_account["balance"] = new_balance

    final_coins = kept_coin_docs + new_coin_docs

    atomic_save_json(ACCOUNTS_PATH, accounts)
    atomic_save_json(ETHANCOIN_PATH, final_coins)

    print()
    print("Done.")
    print(f'"{TARGET_USERNAME}" now has {len(new_balance)} balance entries.')
    print(f"Each new coin has value {TARGET_COIN_VALUE}.")
    print(f"Removed old owned coin docs: {len(deleted_coin_docs)}")
    print(f"Added new coin docs: {len(new_coin_docs)}")
    print()
    print("If anything looks wrong, restore these files from the backup:")
    print(backup_dir)


if __name__ == "__main__":
    main()
