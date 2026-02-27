import express from "express";
import { Client } from "@notionhq/client";
import pkg from "pg";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, "../.env") });
const { Pool } = pkg;

const app = express();
app.use(express.json());

const notion = new Client({
  auth: process.env.NOTION_TOKEN
});


dotenv.config();

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT
});

app.post("/webhook", async (req, res) => {
  try {
    const event = req.body;

    console.log("Webhook received:", event.type);

    if (
      event.type === "page.properties_updated" ||
      event.type === "page.created"
    ) {

      const pageId = event.entity?.id;

      if (!pageId) {
        console.log("No pageId found in event");
        return res.status(200).send("Ignored");
      }

      const page = await notion.pages.retrieve({
        page_id: pageId
      });

      const taskName =
        page.properties["Task Name"]?.title[0]?.plain_text || null;

      const status =
        page.properties.Status?.status?.name || null;

      const dueDate =
        page.properties["Due Date"]?.date?.start || null;

      await pool.query(`
        INSERT INTO tasks (id, task_name, status, due_date, updated_from)
        VALUES ($1, $2, $3, $4, 'notion')
        ON CONFLICT (id)
        DO UPDATE SET
          task_name = EXCLUDED.task_name,
          status = EXCLUDED.status,
          due_date = EXCLUDED.due_date,
          updated_from = 'notion'
      `, [pageId, taskName, status, dueDate]);

      console.log(`Updated Database from Notion | Page: ${pageId} | Status -> ${status}| Due -> ${dueDate}`);
    }

    res.status(200).send("OK");

  } catch (error) {
    console.error("Webhook error:", error);
    res.status(200).send("Error handled"); 
  }
});
setInterval(async () => {

  const result = await pool.query(`
    SELECT * FROM tasks
    WHERE updated_from = 'db'
  `);

  for (const row of result.rows) {

      const formattedDate = row.due_date
      ? row.due_date.toLocaleDateString("en-CA")
      : null;

    await notion.pages.update({
    page_id: row.id,
    properties: {
        Status: {
        status: { name: row.status }
        },
        "Due Date": {
        date: formattedDate
            ? { start: formattedDate }
            : null
        }
    }
    });

    console.log(
      `Updated Notion from Database | Page: ${row.id} | Status -> ${row.status}| Due -> ${formattedDate}`
    );

    await pool.query(
      "UPDATE tasks SET updated_from = NULL WHERE id = $1",
      [row.id]
    );
  }

}, 3000);

app.listen(3000, () => {
  console.log("Server running on port 3000");
});