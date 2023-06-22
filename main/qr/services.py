import hashlib
import qrcode
from io import BytesIO
from django.http import HttpResponse

class QrGenerator():

    def generate_qr_code(reference):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(reference)
        qr.make(fit=True)

        image = qr.make_image(fill='black', back_color='white')
        
        # Create an in-memory file-like object
        byte_stream = BytesIO()
        image.save(byte_stream, format='PNG')
        byte_stream.seek(0)

        # Create a file response
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="qr_code.png"'
        response.write(byte_stream.getvalue())

        return response
    
    def decrypt_qr_code(image_path):
        # Load the QR code image from the specified path
        qr_image = qrcode.image.open(image_path)

        # Convert the QR code image to data
        qr_data = qr_image.get_data()

        # Calculate the MD5 hash of the data
        reference = hashlib.md5(qr_data.encode()).hexdigest()

        return reference