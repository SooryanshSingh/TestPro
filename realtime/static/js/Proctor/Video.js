// Proctor Video (Agora) – Auto-focus first student
// ===============================================

document.addEventListener("DOMContentLoaded", async function () {
    console.log("[PROCTOR] Agora init start");

    const examId = document.getElementById("exam-id").value;
    const videoContainer = document.getElementById("remote-video");

    if (!examId || !videoContainer) {
        console.error("[PROCTOR] Missing examId or video container");
        return;
    }

    // Ensure container has size
    videoContainer.style.width = "100%";
    videoContainer.style.height = "400px";
    videoContainer.style.background = "black";

    // ================================
    // 1️⃣ Fetch Agora Token
    // ================================
    const tokenRes = await fetch(`/agora/token/${examId}/`);
    if (!tokenRes.ok) {
        console.error("[PROCTOR] Failed to fetch Agora token");
        return;
    }

    const { token, appId, channel, uid } = await tokenRes.json();
    console.log("[PROCTOR] Token received", { channel, uid });

    // ================================
    // 2️⃣ Create Agora Client
    // ================================
    const client = AgoraRTC.createClient({
        mode: "rtc",
        codec: "vp8"
    });

    let focusedUser = null;

    // ================================
    // 3️⃣ Join Channel
    // ================================
    await client.join(appId, channel, token, uid);
    console.log("[PROCTOR] Joined Agora channel");

    videoContainer.innerHTML = "<p style='color:white'>Waiting for student...</p>";

    // ================================
    // 4️⃣ Student publishes video
    // ================================
    client.on("user-published", async (user, mediaType) => {
        console.log("[PROCTOR] User published:", user.uid, mediaType);

        if (mediaType !== "video") return;

        // Auto-focus ONLY if none is focused
        if (focusedUser) {
            console.log("[PROCTOR] Already watching someone, ignoring");
            return;
        }

        try {
            await client.subscribe(user, "video");
            console.log("[PROCTOR] Subscribed to video:", user.uid);

            videoContainer.innerHTML = "";
            user.videoTrack.play(videoContainer);

            focusedUser = user;
            console.log("[PROCTOR] Now watching UID:", user.uid);
        } catch (err) {
            console.error("[PROCTOR] Subscribe failed", err);
        }
    });

    // ================================
    // 5️⃣ Student stops / leaves
    // ================================
    function resetView() {
        focusedUser = null;
        videoContainer.innerHTML =
            "<p style='color:white'>Waiting for student...</p>";
    }

    client.on("user-unpublished", user => {
        console.log("[PROCTOR] User unpublished:", user.uid);
        if (focusedUser && focusedUser.uid === user.uid) {
            resetView();
        }
    });

    client.on("user-left", user => {
        console.log("[PROCTOR] User left:", user.uid);
        if (focusedUser && focusedUser.uid === user.uid) {
            resetView();
        }
    });

    console.log("[PROCTOR] Proctor video system ready");
});
