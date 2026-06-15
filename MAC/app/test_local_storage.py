from io import BytesIO
from local_services.local_storage import s3, bucket_name, get_local_file_url

fake_file = BytesIO(b"hello local storage")

s3.upload_fileobj(fake_file, bucket_name, "post-content/test.txt")

print("Uploaded to:", get_local_file_url("post-content/test.txt"))
print("Objects:", s3.list_objects_v2(Bucket=bucket_name, Prefix="post-content"))