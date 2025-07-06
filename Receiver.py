# receiver.py
import json, base64, zlib, os, time
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes

msg = input("✉️ Nhập tin nhắn handshake từ Sender: ")
if msg != "Hello!":
    print("❌ Handshake sai, từ chối kết nối.")
    print("❌ Integrity failed. Gửi NACK về cho Sender.")
    exit()
print("📥 Ready!")

# ====== Bước 1: Tải gói tin ======
with open("packet.json", "r") as f:
    packet = json.load(f)

nonce = base64.b64decode(packet["nonce"])
ciphertext = base64.b64decode(packet["cipher"])
tag = base64.b64decode(packet["tag"])
enc_key = base64.b64decode(packet["enc_key"])
signature = base64.b64decode(packet["sig"])
metadata = packet["metadata"]
received_hash = packet["hash"]

# ====== Bước 2: Kiểm tra toàn vẹn ======
recomputed_hash = SHA512.new(nonce + ciphertext + tag).hexdigest()
if recomputed_hash != received_hash:
    print("❌ Lỗi toàn vẹn! (hash mismatch)")
    print("❌ Integrity failed. Gửi NACK về cho Sender.")
    exit()

# ====== Bước 3: Kiểm tra chữ ký ======
metadata_hash = SHA512.new(metadata.encode())
sender_pubkey = RSA.import_key(open("Keys/Sender_pub.pem").read())
try:
    pkcs1_15.new(sender_pubkey).verify(metadata_hash, signature)
except (ValueError, TypeError):
    print("❌ Chữ ký không hợp lệ!")
    print("❌ Integrity failed. Gửi NACK về cho Sender.")
    exit()

# ====== Bước 4: Giải mã session_key bằng RSA ======
receiver_prikey = RSA.import_key(open("Keys/Receiver_pri.pem").read())
rsa_cipher = PKCS1_v1_5.new(receiver_prikey)
session_key = rsa_cipher.decrypt(enc_key, get_random_bytes(16))

# ====== Bước 5: Giải mã AES-GCM ======
aes = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
try:
    decrypted_data = aes.decrypt_and_verify(ciphertext, tag)
except ValueError:
    print("❌ Xác thực tag thất bại!")
    print("❌ Integrity failed. Gửi NACK về cho Sender.")
    exit()

# ====== Bước 6: Kiểm tra timestamp trong metadata ======
filename, timestamp_str, filetype = metadata.split("|")
timestamp = int(timestamp_str)
current_time = int(time.time())
if abs(current_time - timestamp) > 60:
    print("⚠️ Cảnh báo: Gói tin có thể bị tấn công replay (timestamp không hợp lệ)")
    print("❌ Integrity failed. Gửi NACK về cho Sender.")
    exit()

# ====== Bước 7: Giải nén và lưu ======
plain_data = zlib.decompress(decrypted_data)
os.makedirs("uploads", exist_ok=True)
with open("uploads/received_finance.txt", "wb") as f:
    f.write(plain_data)

# ====== Bước 8: Phản hồi thành công ======
print("✅ Đã giải mã và lưu file: uploads/received_finance.txt")
print("✅ File hợp lệ. ACK gửi lại cho Sender.")
