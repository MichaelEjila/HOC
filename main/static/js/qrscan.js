const video = document.getElementById('video');
const scanBtn = document.getElementById('scan-btn');
const appeard1 = document.getElementById('appd1');
const appeard2 = document.getElementById('appd2');
appeard2.style.display = 'none';


document.getElementById('scannedhash').style.display = 'none';
document.getElementById('BlockHsh-success').style.display = 'none';
document.getElementById('BlockHsh-loading').style.display = 'none';
document.getElementById('video').style.display = 'none';


scanBtn.addEventListener('click', () => {
    scanQRCode();
});

function scanQRCode() {

    document.getElementById('video').style.display = 'block';
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
                if (qrCode != "") {

                    appeard1.style.display = 'none';
                    appeard2.style.display = 'block';
                }
                const vidclose = document.getElementById('video');
                // document.getElementById('login-form').submit();
                vidclose.style.display = 'none';
                document.getElementById('scannedhash').style.display = 'block';
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