// dragSelection.js
let selectedCells = [];
let isMouseDown = false;
let startCell = null;

export function startSelection(event) {
    if (event.target.classList.contains("hour-cell")) return; // 시간을 나타내는 셀은 선택 불가
    isMouseDown = true;
    selectedCells = [];
    clearSelection();
    startCell = event.target; // 시작점 저장
    event.target.classList.add("selected");
    selectedCells.push(event.target);
}

export function selectCell(event) {
    if (isMouseDown && !event.target.classList.contains("hour-cell")) {
        clearSelection(); // 기존 선택 제거
        selectedCells = getCellsInRange(startCell, event.target); // 범위 내 셀 선택
        selectedCells.forEach(cell => cell.classList.add("selected"));
    }
}

export function endSelection() {
    isMouseDown = false;
}

export function clearSelection() {
    document.querySelectorAll(".selected").forEach(cell => {
        cell.classList.remove("selected");
    });
}

export function getCellsInRange(start, end) {
    let cells = Array.from(document.querySelectorAll("#time-table td:not(.hour-cell)"));
    let startIndex = cells.indexOf(start);
    let endIndex = cells.indexOf(end);
    
    if (startIndex > endIndex) [startIndex, endIndex] = [endIndex, startIndex]; // 순서 조정
    return cells.slice(startIndex, endIndex + 1);
}
