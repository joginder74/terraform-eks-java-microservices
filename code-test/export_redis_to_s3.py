import redis
import boto3
import json
import csv
import os
from io import StringIO

# ENV variables to be set in the cloud environment
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
S3_BUCKET = os.getenv("jogi-test11")
EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "json").lower()  # json or csv
S3_KEY = os.getenv("S3_OBJECT_KEY", "redis-dump.json")

# Connect to Redis
def connect_redis():
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Export data from Redis
def fetch_all_data(redis_client):
    data = {}
    for key in redis_client.keys("*"):
        data[key] = redis_client.get(key)
    return data

# Convert data to desired format
def convert_data(data, format_type):
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Key", "Value"])
        for k, v in data.items():
            writer.writerow([k, v])
        return output.getvalue()
    else:
        raise ValueError("Unsupported format. Use 'json' or 'csv'.")

# Upload to S3
def upload_to_s3(data_str):
    s3 = boto3.client("s3")
    s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=data_str)
    print(f"✅ Uploaded data to s3://jogi-test11/{S3_KEY}")

# Main function
def main():
    redis_client = connect_redis()
    data = fetch_all_data(redis_client)
    formatted_data = convert_data(data, EXPORT_FORMAT)
    upload_to_s3(formatted_data)

if __name__ == "__main__":
    main()
