const video = document.getElementById('video');
const scanBtn = document.getElementById('scan-btn');

scanBtn.addEventListener('click', () => {
    scanQRCode();
});

function scanQRCode() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();
            startScanning();
        })
        .catch(function (error) {
            console.error('Error accessing the camera:', error);
        });
}

function startScanning() {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    function scanFrame() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "dontInvert" });

            if (code) {
                video.pause();
                const qrCode = code.data;
                document.getElementById('qr_code_input').value = qrCode;
                const vidclose = document.getElementById('video');
                // document.getElementById('login-form').submit();
                vidclose.style.display = 'none';
                proceed('BlockHsh');
            } else {
                requestAnimationFrame(scanFrame);
            }
        } else {
            requestAnimationFrame(scanFrame);
        }
    }

    requestAnimationFrame(scanFrame);
}