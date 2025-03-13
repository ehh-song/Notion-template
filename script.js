// 24x6 테이블 만들기
const table = document.getElementById("time-table");
const activitySelect = document.getElementById("activity-select");
const applyBtn = document.getElementById("apply-btn");

let selectedCells = [];
let isMouseDown = false;

// 상단 행 (10분 단위)
let headerRow = table.insertRow();
headerRow.insertCell(); // 빈 칸
for (let j = 0; j < 6; j++) {
    let cell = headerRow.insertCell();
    cell.textContent = `${j * 10}`.padStart(2, "0");
}

// 시간 테이블 만들기
for (let i = 6; i < 30; i++) {
    let row = table.insertRow();
    let hourCell = row.insertCell();
    let hour = i % 24;
    hourCell.textContent = `${hour}:00`;

    for (let j = 0; j < 6; j++) {
        let cell = row.insertCell();
        let minutes = j * 10;
        cell.dataset.time = `${hour}:${minutes.toString().padStart(2, "0")}`;
        cell.addEventListener("mousedown", startSelection);
        cell.addEventListener("mouseover", selectCell);
        cell.addEventListener("mouseup", endSelection);
    }
}

// 🎯 드래그 선택 기능
function startSelection(event) {
    isMouseDown = true;
    selectedCells = [];
    clearSelection();
    event.target.classList.add("selected");
    selectedCells.push(event.target);
    console.log(selectedCells)
}
function selectCell(event) {
    if (isMouseDown && !selectedCells.includes(event.target)) {
        event.target.classList.add("selected");
        selectedCells.push(event.target);
    }
}
function endSelection() {
    isMouseDown = false;
}

// 🚀 선택 취소 기능
function clearSelection() {
    document.querySelectorAll(".selected").forEach(cell => {
        cell.classList.remove("selected");
    });
}

// 🎨 선택한 활동 적용 기능
document.getElementById("apply-btn").addEventListener("click", () => {
    
    if (selectedCells.length === 0) {
        console.log('dkdk');
        return;
    }
    let selectedActivity = activitySelect.value;
    let selectedColor = activitySelect.options[activitySelect.selectedIndex].getAttribute("data-color");

    selectedCells.forEach(cell => {
        cell.style.backgroundColor = selectedColor;
        cell.dataset.activity = selectedActivity;
    });

    selectedCells = []; // 적용 후 선택 해제
});
