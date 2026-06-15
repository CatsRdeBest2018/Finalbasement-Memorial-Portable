from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

from pymongo import MongoClient
from bson import ObjectId


# Put your full MongoDB connection string here.
MONGO_URI = 'mongodb+srv://CatsRdeBest2018:Midv1lle!@ethanmongo.3qic3.mongodb.net/TestBot?retryWrites=true&w=majority'

# Your main project database.
DATABASE_NAME = "Finalbasement"

# If True, exports every collection found in the database.
# If False, exports only COLLECTIONS_TO_EXPORT.
EXPORT_ALL_COLLECTIONS = True

COLLECTIONS_TO_EXPORT = [
    "Accounts",
    "Sessions",
    "Randoms",
    "Posts",
    "Articles",
    "Submissions",
    "Suggestions",
    "Archives",
    "Schedules",
    "EthanCoin",
    "Bounties",
    "Trades",
    "Items",
    "Lottery",
]

APP_DIR = Path(__file__).resolve().parent
LOCAL_DB_DIR = APP_DIR / "local_data" / "db"


def convert_mongo_value(value):
    """
    Recursively convert Mongo/Python objects into normal JSON-safe values.

    ObjectId -> string
    datetime -> ISO string
    dict/list -> recursively converted
    """
    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, datetime):
        # Store dates as ISO strings.
        # Example: 2024-02-22T14:04:24.422000+00:00
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()

    if isinstance(value, list):
        return [convert_mongo_value(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): convert_mongo_value(item)
            for key, item in value.items()
        }

    return value


def backup_existing_local_db():
    if not LOCAL_DB_DIR.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = APP_DIR / "local_data" / f"db_backup_{timestamp}"

    shutil.copytree(LOCAL_DB_DIR, backup_dir)
    return backup_dir


def export_collection(db, collection_name):
    collection = db[collection_name]
    documents = list(collection.find({}))

    converted_documents = [
        convert_mongo_value(doc)
        for doc in documents
    ]

    output_path = LOCAL_DB_DIR / f"{collection_name}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(converted_documents, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(converted_documents)} documents -> {output_path}")


def main():
    print("Backing up existing local_data/db folder...")
    backup_dir = backup_existing_local_db()

    if backup_dir:
        print(f"Backup created at: {backup_dir}")
    else:
        print("No existing local db folder found. Skipping backup.")

    print()
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)

    db = client[DATABASE_NAME]

    if EXPORT_ALL_COLLECTIONS:
        collection_names = db.list_collection_names()
    else:
        collection_names = COLLECTIONS_TO_EXPORT

    print(f"Found {len(collection_names)} collections to export.")
    print()

    LOCAL_DB_DIR.mkdir(parents=True, exist_ok=True)

    for collection_name in collection_names:
        export_collection(db, collection_name)

    print()
    print("Mongo export complete.")
    print(f"Local database files saved in: {LOCAL_DB_DIR}")


if __name__ == "__main__":
    main()