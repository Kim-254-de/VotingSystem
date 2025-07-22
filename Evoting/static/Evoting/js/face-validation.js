// Load face-api models from static folder or CDN
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/app/models'),
]).then(startWebcam);

const video = document.getElementById('webcam');
const canvas = document.getElementById('overlay');
const captureButton = document.getElementById('capture');
const retakeButton = document.getElementById('retake');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('preview');

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            alert("Please allow webcam access");
            console.error(err);
        });
}

captureButton.addEventListener('click', async () => {
    const detection = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions());

    if (detection.length === 0) {
        alert('No face detected. Please ensure your face is clearly visible.');
        return;
    }

    if (detection.length > 1) {
        alert('Multiple faces detected. Please ensure only one person is in the frame.');
        return;
    }

    // Draw and capture photo
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageDataUrl = canvas.toDataURL('image/jpeg');
    previewImage.src = imageDataUrl;
    imageInput.value = imageDataUrl;

    video.style.display = 'none';
    canvas.style.display = 'none';
    retakeButton.style.display = 'inline-block';
    captureButton.style.display = 'none';
    previewImage.style.display = 'inline-block';
});

retakeButton.addEventListener('click', () => {
    previewImage.src = "/static/app/images/default-profile.png";
    imageInput.value = "";
    video.style.display = 'inline-block';
    previewImage.style.display = 'none';
    retakeButton.style.display = 'none';
    captureButton.style.display = 'inline-block';
});
