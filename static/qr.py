import qrcode
import os

phone_number = "+977-9863626914"

try:
    # Generate QR code with tel: link
    qr_tel = qrcode.make(f"tel:{phone_number}")
    save_path_tel = os.path.join(os.getcwd(), "phone_number_tel_qr.png")
    qr_tel.save(save_path_tel)
    print(f"QR code with tel: link saved as {save_path_tel}")

    # Generate QR code with plain phone number text
    qr_plain = qrcode.make(phone_number)
    save_path_plain = os.path.join(os.getcwd(), "phone_number_plain_qr.png")
    qr_plain.save(save_path_plain)
    print(f"QR code with plain phone number saved as {save_path_plain}")

except Exception as e:
    print(f"Failed to generate or save QR codes: {e}")
