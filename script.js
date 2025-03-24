// 24x6 테이블 만들기
const table = document.getElementById("time-table");
const activitySelect = document.getElementById("activity");
const applyBtn = document.getElementById("apply-btn");
const addActivityBtn = document.getElementById("add-activity-btn"); // 활동 추가 버튼
const modal = document.getElementById("activity-modal");
const saveActivityBtn = document.getElementById("save-activity-btn");
const newActivityNameInput = document.getElementById("new-activity-name");
const newActivityColorInput = document.getElementById("new-activity-color");

let selectedCells = [];
let isMouseDown = false;
let startCell = null;

// 🟢 저장된 활동 불러오기
function loadActivities() {
    const savedActivities = JSON.parse(localStorage.getItem("activities")) || [];
    savedActivities.forEach(activity => addActivityToSelect(activity.name, activity.color));
}

// 🔵 활동을 select에 추가하는 함수
function addActivityToSelect(name, color) {
    let newOption = document.createElement("option");
    newOption.value = name;
    newOption.textContent = name;
    newOption.setAttribute("data-color", color);
    activitySelect.appendChild(newOption);
}

// ✅ 페이지 로드 시 저장된 활동 불러오기
loadActivities();

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
    hourCell.classList.add("hour-cell"); // 시간 셀 구분을 위한 클래스 추가

    for (let j = 0; j < 6; j++) {
        let cell = row.insertCell();
        let minutes = j * 10;
        cell.dataset.time = `${hour}:${minutes.toString().padStart(2, "0")}`;
        cell.addEventListener("mousedown", startSelection);
        cell.addEventListener("mouseover", selectCell);
        cell.addEventListener("mouseup", endSelection);
    }
}

// 🎯 드래그 선택 기능 (범위 선택)
function startSelection(event) {
    if (event.target.classList.contains("hour-cell")) return; // 시간을 나타내는 셀은 선택 불가
    
    isMouseDown = true;
    selectedCells = [];
    clearSelection();
    startCell = event.target; // 시작점 저장
    event.target.classList.add("selected");
    selectedCells.push(event.target);
}
function selectCell(event) {
    if (isMouseDown && !event.target.classList.contains("hour-cell")) {
        clearSelection(); // 기존 선택 제거
        selectedCells = getCellsInRange(startCell, event.target); // 범위 내 셀 선택
        selectedCells.forEach(cell => cell.classList.add("selected"));
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

// 🔥 범위 내의 셀들을 가져오는 함수 (시간 셀 제외)
function getCellsInRange(start, end) {
    let cells = Array.from(document.querySelectorAll("#time-table td:not(.hour-cell)")); // 시간 셀 제외
    let startIndex = cells.indexOf(start);
    let endIndex = cells.indexOf(end);
    
    if (startIndex > endIndex) [startIndex, endIndex] = [endIndex, startIndex]; // 순서 조정
    return cells.slice(startIndex, endIndex + 1);
}

// 🎨 선택한 활동 적용 기능 (버튼 클릭 시 색상 변경)
applyBtn.addEventListener("click", () => {
    if (selectedCells.length === 0) {
        console.log("선택된 셀이 없음");
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

// ✅ 활동 추가 버튼을 토글 방식으로 변경
addActivityBtn.addEventListener("click", () => {
    modal.style.display = modal.style.display === "block" ? "none" : "block"; // 토글 방식
});

// 🟠 새 활동 저장 기능 (localStorage에 저장)
saveActivityBtn.addEventListener("click", () => {
    let newActivityName = newActivityNameInput.value.trim();
    let newActivityColor = newActivityColorInput.value;

    if (newActivityName === "") {
        alert("활동 이름을 입력하세요.");
        return;
    }

    // 기존 활동 목록 불러오기
    let activities = JSON.parse(localStorage.getItem("activities")) || [];
    
    // 중복 확인
    if (activities.some(activity => activity.name === newActivityName)) {
        alert("이미 존재하는 활동입니다.");
        return;
    }

    // 새로운 활동 추가
    let newActivity = { name: newActivityName, color: newActivityColor };
    activities.push(newActivity);
    localStorage.setItem("activities", JSON.stringify(activities)); // 저장

    // 드롭다운에 추가
    addActivityToSelect(newActivityName, newActivityColor);
    activitySelect.value = newActivityName; // 방금 추가한 활동을 선택

    // 입력 필드 초기화 후 모달 닫기
    newActivityNameInput.value = "";
    modal.style.display = "none";
});
