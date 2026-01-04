let blurTimeout;

const tab = new WebSocket(`${wsScheme}://${window.location.host}/ws/exam/tab/${examId}/`);

window.addEventListener("blur", function () {
    blurTimeout = setTimeout(() => {
        sendTabChange();
    }, 1000);
});

window.addEventListener("focus", function () {
    clearTimeout(blurTimeout);
});

function sendTabChange() {
    if (tab.readyState === WebSocket.OPEN) {
        tab.send(JSON.stringify({
            type: "tab_change"
        }));
    }
}
