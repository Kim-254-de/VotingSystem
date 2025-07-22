// Load face-api models from static folder or CDN
// Load face-api.js model
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/Evoting/models')
]).then(startWebcam).catch(err => {
    console.error("Model loading failed:", err);
    alert("Failed to load face detection model.");
});

const video = document.getElementById('webcam');
const canvas = document.getElementById('overlay');
const captureButton = document.getElementById('capture');
const retakeButton = document.getElementById('retake');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('preview');

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            alert("Please allow webcam access to capture your photo.");
            console.error("Webcam error:", err);
        });
}

captureButton.addEventListener('click', async () => {
    const detection = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions());

    if (detection.length === 0) {
        alert(' No face detected. Please ensure your face is clearly visible and well-lit.');
        return;
    }

    if (detection.length > 1) {
        alert('Multiple faces detected. Please ensure only you are in front of the camera.');
        return;
    }

    // Draw video to canvas
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get image data URL
    const imageDataUrl = canvas.toDataURL('image/jpeg');
    previewImage.src = imageDataUrl;
    imageInput.value = imageDataUrl;

    // Hide video, show preview
    video.style.display = 'none';
    canvas.style.display = 'none';
    captureButton.style.display = 'none';
    retakeButton.style.display = 'inline-block';
    previewImage.style.display = 'inline-block';
});

retakeButton.addEventListener('click', () => {
    // Reset preview and input
    previewImage.src = "/static/Evoting/images/default-profile.png"; // fallback image
    imageInput.value = "";

    // Show video again
    video.style.display = 'inline-block';
    previewImage.style.display = 'none';
    canvas.style.display = 'none';
    retakeButton.style.display = 'none';
    captureButton.style.display = 'inline-block';
});
