(async function () {
    console.log("[STUDENT] Agora init start");

    const examId = document.getElementById("exam-id").value;

    const res = await fetch(`/agora/token/${examId}/`);
    if (!res.ok) {
        console.error("[STUDENT] Token fetch failed");
        return;
    }

    const { token, appId, channel, uid } = await res.json();
    console.log("[STUDENT] Token OK", { channel, uid });

    const client = AgoraRTC.createClient({
        mode: "rtc",
        codec: "vp8",
    });

    await client.join(appId, channel, token, uid);
    console.log("[STUDENT] Joined channel");

    // 🎥 CREATE CAMERA TRACK
    const localVideoTrack = await AgoraRTC.createCameraVideoTrack();

 

    // 🚀 PUBLISH CAMERA
    await client.publish([localVideoTrack]);
    console.log("[STUDENT] Camera published");
})();
