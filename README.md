# 🔄 Notion Bidirectional Sync System

A full-stack synchronization system between Notion and PostgreSQL.

This project demonstrates:
- Notion API integration
- Webhook handling
- PostgreSQL database management
- Bidirectional data synchronization
- Backend automation with Node.js and Python

---

## 📌 System Architecture

Notion Database  
⬇ (Webhook)  
Node.js Server  
⬇  
PostgreSQL  
⬇ (Polling Sync)  
Notion API  

---

## 🚀 Features

- Sync Notion → PostgreSQL via Webhook
- Sync PostgreSQL → Notion via API polling
- Automatic status and due date updates
- Conflict prevention using `updated_from` flag
- Secure environment variable configuration

---

## 🛠 Tech Stack

- Python (requests, psycopg2)
- Node.js (Express)
- PostgreSQL
- Notion API
- dotenv

---

## 🔑 Environment Setup

Create a `.env` file based on `.env.example`:

```
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id

DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🗄 Database Setup

Run:

```bash
psql -U postgres -d your_db -f schema.sql
```

---

## ▶ Run the Project

### 1️⃣ Start Node Webhook Server

```bash
cd notion-webhook
node server.js
```

### 2️⃣ Run Python Sync Script

```bash
cd notion_sync
python main.py
```

---

## 🎬 Demo Flow

1. Update task in Notion → Webhook updates PostgreSQL  
2. Update task in PostgreSQL → Sync updates Notion  
3. Logs display real-time synchronization  

Example Log:

```
Updated Notion from Database | Page: 3136229d-af67... | Status -> In progress | Due -> 2026-01-05
```

---

## 📂 Project Structure

```
notion-bidirectional-sync
│
├── notion_sync
│   └── main.py
│
├── notion-webhook
│   └── server.js
│
├── requirements.txt
├── schema.sql
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔒 Security
- `.env` ignored via `.gitignore`
- Example configuration provided

