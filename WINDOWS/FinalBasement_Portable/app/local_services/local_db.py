import json
import os
import threading
import uuid
from pathlib import Path
from datetime import datetime

try:
  from bson import ObjectId
except Exception:
  ObjectId = None


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "local_data" / "db"

_DB_LOCK = threading.RLock()


def _normalize_value(value):
  """
  Makes IDs comparable between old Mongo export formats and local strings.

  Examples:
    ObjectId("abc") -> "abc"
    {"$oid": "abc"} -> "abc"
    normal strings stay strings
  """
  if ObjectId is not None and isinstance(value, ObjectId):
    return str(value)

  if isinstance(value, dict) and "$oid" in value:
    return str(value["$oid"])

  return value


def _json_safe(value):
  """
  Converts Python/Mongo objects into JSON-safe values before saving.
  """
  if ObjectId is not None and isinstance(value, ObjectId):
    return str(value)

  if isinstance(value, datetime):
    return value.isoformat()

  if isinstance(value, list):
    return [_json_safe(item) for item in value]

  if isinstance(value, dict):
    return {
      str(key): _json_safe(item)
      for key, item in value.items()
    }

  return value


class LocalCollection:
  def __init__(self, name):
    self.name = name
    self.path = DB_DIR / f"{name}.json"

    DB_DIR.mkdir(parents=True, exist_ok=True)

    if not self.path.exists():
      self._save([])


  def _load(self):
    with _DB_LOCK:
      if not self.path.exists():
        return []

      try:
        with open(self.path, "r", encoding="utf-8") as f:
          content = f.read().strip()

        if content == "":
          return []

        data = json.loads(content)

        if not isinstance(data, list):
          raise RuntimeError(
            f"Local database file must contain a JSON list: {self.path}"
          )

        return data

      except json.JSONDecodeError as e:
        broken_path = self.path.with_suffix(
          self.path.suffix + f".broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        try:
          self.path.rename(broken_path)
        except Exception:
          broken_path = self.path

        raise RuntimeError(
          f"\nLocal database file is corrupted:\n"
          f"{self.path}\n\n"
          f"Broken file moved to:\n"
          f"{broken_path}\n\n"
          f"Restore this collection from a backup or rerun download_mongo.py.\n"
        ) from e


  def _save(self, data):
    with _DB_LOCK:
      safe_data = _json_safe(data)

      self.path.parent.mkdir(parents=True, exist_ok=True)

      temp_path = self.path.with_suffix(
        self.path.suffix + f".tmp_{os.getpid()}_{threading.get_ident()}_{uuid.uuid4().hex}"
      )

      with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(safe_data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())

      os.replace(temp_path, self.path)


  def _get_nested_value(self, document, dotted_key):
    """
    Supports simple dotted keys like:
      active.online
    """
    current = document

    for part in dotted_key.split("."):
      if not isinstance(current, dict):
        return None

      if part not in current:
        return None

      current = current[part]

    return current


  def _set_nested_value(self, document, dotted_key, value):
    """
    Supports simple dotted $set keys like:
      active.online
    """
    current = document
    parts = dotted_key.split(".")

    for part in parts[:-1]:
      if part not in current or not isinstance(current[part], dict):
        current[part] = {}

      current = current[part]

    current[parts[-1]] = value


  def _matches(self, document, query):
    if query is None:
      return True

    for key, expected in query.items():
      actual = self._get_nested_value(document, key)

      actual_normalized = _normalize_value(actual)
      expected_normalized = _normalize_value(expected)

      if actual_normalized != expected_normalized:
        return False

    return True


  def find_one(self, query):
    data = self._load()

    for doc in data:
      if self._matches(doc, query):
        return doc

    return None


  def find(self, query=None):
    data = self._load()

    if query is None:
      return data

    return [
      doc for doc in data
      if self._matches(doc, query)
    ]


  def insert_one(self, document):
    data = self._load()

    if "_id" not in document:
      document["_id"] = uuid.uuid4().hex

    data.append(document)
    self._save(data)

    return {
      "inserted_id": document["_id"]
    }


  def update_one(self, query, update):
    data = self._load()

    for doc in data:
      if self._matches(doc, query):

        if "$set" in update:
          for key, value in update["$set"].items():
            self._set_nested_value(doc, key, value)

        if "$push" in update:
          for key, value in update["$push"].items():
            current_list = self._get_nested_value(doc, key)

            if current_list is None:
              self._set_nested_value(doc, key, [])
              current_list = self._get_nested_value(doc, key)

            if not isinstance(current_list, list):
              raise RuntimeError(
                f"Cannot $push into non-list field '{key}' in collection '{self.name}'"
              )

            current_list.append(value)

        if "$pull" in update:
          for key, value in update["$pull"].items():
            current_list = self._get_nested_value(doc, key)

            if current_list is None:
              continue

            if not isinstance(current_list, list):
              raise RuntimeError(
                f"Cannot $pull from non-list field '{key}' in collection '{self.name}'"
              )

            pulled_value = _normalize_value(value)

            new_list = []
            for item in current_list:
              if isinstance(item, dict) and isinstance(value, dict):
                should_remove = True

                for value_key, value_expected in value.items():
                  item_actual = item.get(value_key)

                  if _normalize_value(item_actual) != _normalize_value(value_expected):
                    should_remove = False
                    break

                if not should_remove:
                  new_list.append(item)

              else:
                if _normalize_value(item) != pulled_value:
                  new_list.append(item)

            self._set_nested_value(doc, key, new_list)

        self._save(data)

        return {
          "matched_count": 1,
          "modified_count": 1
        }

    return {
      "matched_count": 0,
      "modified_count": 0
    }


  def delete_one(self, query):
    data = self._load()

    for index, doc in enumerate(data):
      if self._matches(doc, query):
        deleted = data.pop(index)
        self._save(data)

        return {
          "deleted_count": 1,
          "deleted_document": deleted
        }

    return {
      "deleted_count": 0
    }


  def count_documents(self, query=None):
    return len(self.find(query))


# Main FinalBasement collections
Accounts = LocalCollection("Accounts")
Sessions = LocalCollection("Sessions")
Randoms = LocalCollection("Randoms")
Posts = LocalCollection("Posts")
Articles = LocalCollection("Articles")
Submissions = LocalCollection("Submissions")
Suggestions = LocalCollection("Suggestions")
Archives = LocalCollection("Archives")
Schedules = LocalCollection("Schedules")

# EthanCoin collections
EthanCoin = LocalCollection("EthanCoin")
Bounties = LocalCollection("Bounties")
Trades = LocalCollection("Trades")
Items = LocalCollection("Items")
Lottery = LocalCollection("Lottery")