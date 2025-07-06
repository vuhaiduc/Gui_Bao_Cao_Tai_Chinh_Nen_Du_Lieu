from Crypto.PublicKey import RSA

# Tạo key cho Sender
sender_key = RSA.generate(1024)
with open("Keys/Sender_pri.pem", "wb") as f:
    f.write(sender_key.export_key(format='PEM'))  # PKCS#8 mặc định
with open("Keys/Sender_pub.pem", "wb") as f:
    f.write(sender_key.publickey().export_key())

# Tạo key cho Receiver
receiver_key = RSA.generate(1024)
with open("Keys/Receiver_pri.pem", "wb") as f:
    f.write(receiver_key.export_key(format='PEM'))  # PKCS#8 mặc định
with open("Keys/Receiver_pub.pem", "wb") as f:
    f.write(receiver_key.publickey().export_key())

print("✅ Đã tạo xong các khóa RSA ở thư mục Keys/")
