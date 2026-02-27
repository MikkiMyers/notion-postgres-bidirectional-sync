import os
import requests
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ===== Notion Config =====
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# ===== PostgreSQL Config =====
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# ===== Notion Headers =====
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# ===== Connect to PostgreSQL =====
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

print("Starting Notion and Database Sync...")

# ===== Fetch from Notion =====
url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

has_more = True
next_cursor = None

while has_more:
    payload = {}
    if next_cursor:
        payload["start_cursor"] = next_cursor

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    
    if response.status_code != 200:
        print("Error fetching from Notion:", response.status_code, response.text)
        break
    data = response.json()

    for page in data.get("results", []):
        try:
            page_id = page["id"]
            properties = page["properties"]

            # ===== Extract Fields =====
            title_list = properties["Task Name"]["title"]
            task_name = title_list[0]["plain_text"] if title_list else None

            status = properties["Status"]["status"]["name"]

            due = properties["Due Date"]["date"]
            due_date = due["start"] if due else None

            notion_last_edited_str = page["last_edited_time"]
            notion_last_edited = datetime.fromisoformat(
                notion_last_edited_str.replace("Z", "+00:00")
            ).replace(tzinfo=None)

            # ===== Check if exists in DB =====
            cursor.execute(
                "SELECT task_name, status, due_date, last_edited FROM tasks WHERE id = %s",
                (page_id,)
            )
            result = cursor.fetchone()

            if result:
                db_task_name, db_status, db_due_date, db_last_edited = result

                if db_last_edited and db_last_edited > notion_last_edited:
                    print(f"Updating Notion from DB: {db_task_name}")

                    update_url = f"https://api.notion.com/v1/pages/{page_id}"

                    update_payload = {
                        "properties": {
                            "Task Name": {
                                "title": [
                                    {
                                        "text": {
                                            "content": db_task_name
                                        }
                                    }
                                ]
                            },
                            "Status": {
                                "status": {
                                    "name": db_status
                                }
                            }
                        }
                    }

                    update_response = requests.patch(
                        update_url,
                        headers=headers,
                        json=update_payload,
                        timeout=10
                    )
                    if update_response.status_code != 200:
                        print("Error updating Notion:", update_response.status_code, update_response.text)
                    continue

            # ===== Insert / Update DB =====
            cursor.execute("""
                INSERT INTO tasks (id, task_name, status, due_date, last_edited)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    task_name = EXCLUDED.task_name,
                    status = EXCLUDED.status,
                    due_date = EXCLUDED.due_date,
                    last_edited = EXCLUDED.last_edited;
            """, (page_id, task_name, status, due_date, notion_last_edited))

            print(f"Synced to DB: {task_name}")

        except Exception as e:
            print("Error processing page:", e)

    has_more = data.get("has_more", False)
    next_cursor = data.get("next_cursor")

conn.commit()
cursor.close()
conn.close()

print("Bi-Directional Sync Completed.")