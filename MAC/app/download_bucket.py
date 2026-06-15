from pathlib import Path
import boto3
from botocore.exceptions import ClientError


BUCKET_NAME = "finalbasementbucket"
AWS_ACCESS_KEY_ID = 'AKIA6GBMGJCFQ4BCN7HH'
AWS_SECRET_ACCESS_KEY = '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'
REGION_NAME = 'us-east-2'

DOWNLOAD_DIR = Path("local_data/files")


def download_bucket():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
    )

    paginator = s3.get_paginator("list_objects_v2")
    total = 0

    try:
        for page in paginator.paginate(Bucket=BUCKET_NAME):
            objects = page.get("Contents", [])

            if not objects:
                print("No files found in bucket.")
                return

            for obj in objects:
                key = obj["Key"]

                if key.endswith("/"):
                    continue

                local_path = DOWNLOAD_DIR / key
                local_path.parent.mkdir(parents=True, exist_ok=True)

                print(f"Downloading {key} -> {local_path}")
                s3.download_file(BUCKET_NAME, key, str(local_path))

                total += 1

        print()
        print(f"Done. Downloaded {total} files.")
        print(f"Saved to: {DOWNLOAD_DIR.resolve()}")

    except ClientError as e:
        print("AWS error:")
        print(e)


if __name__ == "__main__":
    download_bucket()