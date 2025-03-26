// server.js
const express = require('express');
const fetch = require('node-fetch');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(express.static('public')); // public 폴더에서 클라이언트 HTML, JS 제공

const notionDatabaseId = process.env.NOTION_DATABASE_ID; // .env 파일에서 가져오기
const notionApiKey = process.env.NOTION_API_KEY; // .env 파일에서 가져오기

// 클라이언트에서 /save-to-notion으로 POST 요청 받기
app.post('/save-to-notion', async (req, res) => {
    const { date, time, activity } = req.body;

    // Notion API에 페이지 추가 요청
    const response = await fetch("https://api.notion.com/v1/pages", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${notionApiKey}`,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        },
        body: JSON.stringify({
            parent: { database_id: notionDatabaseId },
            properties: {
                "날짜": { date: { start: date } },
                "시간": { title: [{ text: { content: time } }] },
                "항목": { select: { name: activity } }
            }
        })
    });

    if (response.ok) {
        res.json({ message: "Notion에 기록 성공!" });
    } else {
        res.status(500).json({ message: "Notion 기록 실패", error: await response.json() });
    }
});

app.listen(5000, () => {
    console.log("Server is running on http://localhost:5000");
});
