function openModal(modalId) {
    const modal = document.getElementById(modalId + '-modal');
    if (modalId == "make-qr") {
        const dis2 = document.getElementById('OpenticketQR');
        dis2.style.display = 'none';
    }
    modal.style.display = 'block';
}

function proceed(modalId) {
    const getvalue = document.getElementById(modalId);
    const loadingIcon = document.getElementById(modalId + '-loading');
    const successMessage = document.getElementById(modalId + '-success');
    const dis1 = document.getElementById('mkT');

    loadingIcon.style.display = 'block';

    if (modalId == "BlockHsh") {
        // document.getElementById('login-form').submit();
        setTimeout(function () {
            loadingIcon.style.display = 'none';
            successMessage.style.display = 'block';
        }, 5000);


        setTimeout(function () {
            closeModal('scan-qr');
        }, 8000);
    }
    else if (modalId == "make-qr") {
        // document.getElementById('makeTicket').submit();
        const dis2 = document.getElementById('OpenticketQR');
        setTimeout(function () {
            dis1.style.display = 'none';
            loadingIcon.style.display = 'none';
            successMessage.style.display = 'block';
            dis2.style.display = 'block';

        }, 5000);


        //   setTimeout(function () {

        //     closeModal('make-qr');
        //   }, 3000);
    }

}
function closeModal(modalId) {
    const modal = document.getElementById(modalId + '-modal');
    modal.style.display = 'none';
}


function SendEUNU(request) {
    document.getElementById(request).submit();

}