const tableBody = document.getElementById("student-table");

const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(
    `${wsScheme}://${window.location.host}/ws/exam/tab/${EXAM_ID}/`
);

/*
 full_session_id → {
   countCell
 }
*/
const students = {};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (!["student_joined", "violation_update"].includes(data.type)) return;

    const maskedId = data.masked_session_id;
    const fullSessionId = data.full_session_id;
    const count = data.violation_count;

    if (!fullSessionId) {
        console.warn("Missing fullSessionId", data);
        return;
    }

    if (!students[fullSessionId]) {
        const row = document.createElement("tr");

        const sessionCell = document.createElement("td");
        sessionCell.innerText = maskedId;

        const countCell = document.createElement("td");
        countCell.innerText = count;

        row.style.cursor = "pointer";
        row.title = "Click to open proctor view";

        row.onclick = () => {
            console.log("[PROCTOR] Opening session:", fullSessionId);

            window.open(
                `/proctor/${EXAM_ID}/session/${fullSessionId}/data`,
                "_blank"
            );
        };

        row.appendChild(sessionCell);
        row.appendChild(countCell);
        tableBody.appendChild(row);

        students[fullSessionId] = { countCell };
    }

    students[fullSessionId].countCell.innerText = count;
};

socket.onopen = () => {
    console.log("[PROCTOR] Dashboard WS connected");
};

socket.onclose = () => {
    console.log("[PROCTOR] Dashboard WS disconnected");
};
