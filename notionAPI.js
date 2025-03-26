// notionAPI.js
export async function addToNotionDatabase(date, time, activity) {
    const notionApiKey = process.env.NOTION_API_KEY;  // .env에서 가져오기
    const notionDatabaseId = process.env.NOTION_DATABASE_ID;  // .env에서 가져오기

    const response = await fetch("http://localhost:5000/save-to-notion", {
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
        console.log("✅ Notion에 기록 성공!");
    } else {
        console.error("❌ Notion 기록 실패:", await response.json());
    }
}
