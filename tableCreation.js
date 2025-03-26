// tableCreation.js
export function createTable(table) {
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
}

export function addActivityToSelect(activitySelect, name, color) {
    let newOption = document.createElement("option");
    newOption.value = name;
    newOption.textContent = name;
    newOption.setAttribute("data-color", color);
    activitySelect.appendChild(newOption);
}
