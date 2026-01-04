document.addEventListener("DOMContentLoaded", function () {
 
    const timerDisplay = document.getElementById("timer");
    
    function updateTimer() {
        fetch(`/get_remaining_time/${examId}/`)
            .then(response => response.json())
            .then(data => {
                let timeLeft = Math.floor(data.remaining_time);
                if (timeLeft <= 120) {
                        timerDisplay.style.color = "red";
                        timerDisplay.style.fontWeight = "bold";
}
                if (timeLeft <= 0) {
                    window.location.href = window.TEST_END_URL;
                    clearInterval(timerInterval);
                } else {
                    let minutes = Math.floor(timeLeft / 60);
                    let seconds = timeLeft % 60;
                    timerDisplay.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                }   
            })
            .catch(error => console.error("Error fetching timer:", error));
    }
    
    updateTimer();  
    const timerInterval = setInterval(updateTimer, 1000);
    });
    