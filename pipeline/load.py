import os
import pandas as pd
from pymongo import MongoClient, errors


def transform_and_load(scraped_data):
    """
    Transforms the nested Hacker News dictionary into a flat DataFrame
    and loads it into MongoDB.
    """
    # 1. Flatten the data for Pandas
    # We want a row for every thread, including its list of comments
    flattened_records = []

    for category, threads in scraped_data.items():
        for thread in threads:
            record = {
                "category": category,
                "hn_id": thread.get("id"),
                "title": thread.get("title"),
                "link": thread.get("link"),
                "points": int(thread.get("points", 0)),
                "comment_count": int(thread.get("comments_count", 0)),
                "top_comments": thread.get("top_comments", []),
                "extracted_at": pd.Timestamp.now()
            }
            flattened_records.append(record)

    df = pd.DataFrame(flattened_records)

    # 2. Data Cleaning/Validation with Pandas
    # Ensure no duplicates if we're running this across different categories
    df = df.drop_duplicates(subset=['hn_id'])

    print(f"[*] Prepared {len(df)} unique threads for database load.")

    # 3. MongoDB Ingestion
    try:
        db_uri = os.getenv("MONGO_URI", "mongodb://admin:password@pipeline-db:27017/")
        client = MongoClient(db_uri, serverSelectionTimeoutMS=5000)
        db = client["pipeline-db"]
        collection = db["threads"]

        # Convert DataFrame to list of dictionaries for MongoDB
        data_to_insert = df.to_dict(orient='records')

        if data_to_insert:
            # Use upsert logic (update if exists, insert if not) based on hn_id
            for record in data_to_insert:
                collection.update_one(
                    {"hn_id": record["hn_id"]},
                    {"$set": record},
                    upsert=True
                )
            print("[+] Successfully synced data to MongoDB (Database: pipeline-db, Collection: threads)")

    except errors.ServerSelectionTimeoutError:
        print("[!] Could not connect to MongoDB. Check if your instance is running.")
    except Exception as e:
        print(f"[!] An error occurred during DB load: {e}")
    finally:
        client.close()