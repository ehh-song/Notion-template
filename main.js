// main.js
import { startSelection, selectCell, endSelection, clearSelection, getCellsInRange } from './dragSelection.js';
import { createTable, addActivityToSelect } from './tableCreation.js';
import { addToNotionDatabase } from './notionAPI.js';
import { loadActivities, saveActivity } from './activityStorage.js';

// DOM 요소들
const table = document.getElementById("time-table");
const activitySelect = document.getElementById("activity");
const applyBtn = document.getElementById("apply-btn");
const addActivityBtn = document.getElementById("add-activity-btn"); 
const modal = document.getElementById("activity-modal");
const saveActivityBtn = document.getElementById("save-activity-btn");
const newActivityNameInput = document.getElementById("new-activity-name");
const newActivityColorInput = document.getElementById("new-activity-color");

// 테이블 및 활동 불러오기
createTable(table);
loadActivities(activitySelect);

// 버튼 이벤트 리스너
applyBtn.addEventListener("click", () => {
    if (selectedCells.length === 0) {
        console.log("선택된 셀이 없음");
        return;
    }
    let selectedActivity = activitySelect.value;
    let selectedColor = activitySelect.options[activitySelect.selectedIndex].getAttribute("data-color");
    let selectedDate = new Date().toISOString().split("T")[0];

    // 시작 시간과 종료 시간 계산
    let times = selectedCells.map(cell => cell.dataset.time);
    times.sort();
    let startTime = times[0];
    let endTime = times[times.length - 1];
    let timeRange = `${startTime} - ${endTime}`;

    selectedCells.forEach(cell => {
        cell.style.backgroundColor = selectedColor;
        cell.dataset.activity = selectedActivity;
    });

    console.log("✅ Notion API 호출 전", timeRange, selectedDate, selectedActivity);

    // ✅ Notion 데이터베이스에 저장
    addToNotionDatabase(selectedDate, timeRange, selectedActivity);

    selectedCells = []; // 적용 후 선택 해제
});

// 새 활동 저장
saveActivityBtn.addEventListener("click", () => {
    let newActivityName = newActivityNameInput.value.trim();
    let newActivityColor = newActivityColorInput.value;

    if (newActivityName === "") {
        alert("활동 이름을 입력하세요.");
        return;
    }

    let newActivity = saveActivity(newActivityName, newActivityColor);
    addActivityToSelect(activitySelect, newActivity.name, newActivity.color);
    newActivityNameInput.value = "";
    modal.style.display = "none";
});
