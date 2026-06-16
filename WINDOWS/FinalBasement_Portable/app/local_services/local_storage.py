# local_services/local_storage.py

from pathlib import Path
import shutil
import base64
import mimetypes

BASE_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = BASE_DIR / "local_data" / "files"


class LocalS3Client:
    def __init__(self):
        FILES_DIR.mkdir(parents=True, exist_ok=True)

    def _path_from_key(self, key):
        # Prevent weird absolute path issues
        key = key.replace("\\", "/").lstrip("/")
        return FILES_DIR / key

    def upload_fileobj(self, fileobj, bucket_name, key, ExtraArgs=None):
        path = self._path_from_key(key)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            fileobj.seek(0)
            shutil.copyfileobj(fileobj, f)

        return True

    def list_objects_v2(self, Bucket, Prefix=""):
        folder = self._path_from_key(Prefix)

        contents = []

        if folder.exists():
            for path in folder.rglob("*"):
                if path.is_file():
                    relative_key = path.relative_to(FILES_DIR).as_posix()
                    contents.append({"Key": relative_key})

        return {"Contents": contents}

    def delete_object(self, Bucket, Key):
        path = self._path_from_key(Key)

        if path.exists():
            path.unlink()

        return True

    def get_object(self, Bucket, Key):
        path = self._path_from_key(Key)

        return {
            "Body": open(path, "rb")
        }


bucket_name = "local-finalbasement-bucket"
region_name = "local"

s3 = LocalS3Client()

def get_local_file_url(key):
    key = key.replace("\\", "/").lstrip("/")
    return f"local_data/files/{key}"

def s3_url_to_local_path(url_or_path):
    if not isinstance(url_or_path, str):
        return url_or_path

    old_prefix = "https://finalbasementbucket.s3.us-east-2.amazonaws.com/"
    if url_or_path.startswith(old_prefix):
        key = url_or_path[len(old_prefix):]
        return get_local_file_url(key)

    return url_or_path

def local_path_to_key(path_or_url):
    if not isinstance(path_or_url, str):
        return path_or_url

    path_or_url = path_or_url.replace("\\", "/")

    old_prefix = "https://finalbasementbucket.s3.us-east-2.amazonaws.com/"
    if path_or_url.startswith(old_prefix):
        return path_or_url[len(old_prefix):]

    local_prefix = "local_data/files/"
    if path_or_url.startswith(local_prefix):
        return path_or_url[len(local_prefix):]

    return path_or_url.lstrip("/")

def get_display_image_src(path_or_url):
    if not isinstance(path_or_url, str):
        return path_or_url

    converted = s3_url_to_local_path(path_or_url)

    # If it is still some normal web URL, leave it alone.
    if converted.startswith("http://") or converted.startswith("https://"):
        return converted

    local_path = Path(converted)

    # Make relative paths work from the app root.
    if not local_path.is_absolute():
        local_path = BASE_DIR / local_path

    if not local_path.exists():
        return converted

    mime_type, _ = mimetypes.guess_type(local_path.name)
    if mime_type is None:
        mime_type = "image/png"

    encoded = base64.b64encode(local_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"