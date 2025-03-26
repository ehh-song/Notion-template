// activityStorage.js
export function loadActivities(activitySelect) {
    const savedActivities = JSON.parse(localStorage.getItem("activities")) || [];
    savedActivities.forEach(activity => addActivityToSelect(activitySelect, activity.name, activity.color));
}

export function saveActivity(newActivityName, newActivityColor) {
    let activities = JSON.parse(localStorage.getItem("activities")) || [];
    if (activities.some(activity => activity.name === newActivityName)) {
        alert("이미 존재하는 활동입니다.");
        return;
    }

    let newActivity = { name: newActivityName, color: newActivityColor };
    activities.push(newActivity);
    localStorage.setItem("activities", JSON.stringify(activities)); // 저장
    return newActivity;
}
