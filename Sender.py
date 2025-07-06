# sender.py
import zlib, json, base64, time
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes

print("📤 Hello!")  # Gửi Hello
# Đợi phản hồi từ Receiver (mô phỏng)
input("⏳ Đợi Receiver phản hồi Ready... (ấn Enter để tiếp tục)")


# ====== Bước 1: Chuẩn bị ======
filename = "Input/finance.txt"
filetype = "text/plain"
timestamp = str(int(time.time()))

# Đọc nội dung gốc
with open("Input/finance.txt", "rb") as f:
    original_data = f.read()

# ====== Bước 2: Tạo khóa ======
session_key = get_random_bytes(16)
nonce = get_random_bytes(12)

# ====== Bước 3: Nén ======
compressed_data = zlib.compress(original_data)

# ====== Bước 4: Mã hóa AES-GCM ======
cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
ciphertext, tag = cipher.encrypt_and_digest(compressed_data)

# ====== Bước 5: Mã hóa session_key bằng RSA ======
receiver_pubkey = RSA.import_key(open("Keys/Receiver_pub.pem").read())
rsa_cipher = PKCS1_v1_5.new(receiver_pubkey)
encrypted_key = rsa_cipher.encrypt(session_key)

# ====== Bước 6: Ký metadata ======
metadata = f"{filename}|{timestamp}|{filetype}"
metadata_hash = SHA512.new(metadata.encode())
private_key = RSA.import_key(open("Keys/Sender_pri.pem").read())
signature = pkcs1_15.new(private_key).sign(metadata_hash)

# ====== Bước 7: Hash toàn vẹn ======
full_hash = SHA512.new(nonce + ciphertext + tag).hexdigest()

# ====== Bước 8: Gói tin ======
packet = {
    "nonce": base64.b64encode(nonce).decode(),
    "cipher": base64.b64encode(ciphertext).decode(),
    "tag": base64.b64encode(tag).decode(),
    "hash": full_hash,
    "sig": base64.b64encode(signature).decode(),
    "enc_key": base64.b64encode(encrypted_key).decode(),
    "metadata": metadata
}

# Lưu gói tin
with open("packet.json", "w") as f:
    json.dump(packet, f, indent=2)

print("✅ Gói tin đã được tạo và lưu vào packet.json")
input("⏳ Chờ ACK/NACK từ Receiver... (ấn Enter sau khi nhận phản hồi)")
