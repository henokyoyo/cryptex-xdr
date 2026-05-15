from Crypto.Cipher import AES
from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2
import os, struct, json

class CryptexDecryptor:
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        return PBKDF2(password.encode(), salt, dkLen=32, count=600000, hmac_hash_module=SHA256)

    @staticmethod
    def decrypt_file(filepath: str, password: str) -> dict:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        salt = data[:32]
        nonce = data[32:44]
        meta_len = struct.unpack('<I', data[44:48])[0]
        meta_bytes = data[48:48+meta_len]
        offset = 48 + meta_len
        tag = data[offset:offset+16]
        hmac_stored = data[offset+16:offset+48]
        ciphertext = data[offset+48:]
        
        key = CryptexDecryptor.derive_key(password, salt)
        
        hmac_check = HMAC.new(key, data[:offset] + ciphertext, SHA256).digest()
        if hmac_check != hmac_stored:
            raise ValueError("INTEGRITY CHECK FAILED")
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except:
            raise ValueError("DECRYPTION FAILED - Wrong password")
        
        metadata = json.loads(meta_bytes.decode())
        
        output_path = filepath.replace('.cryptex', '')
        final_path = output_path
        
        counter = 1
        while os.path.exists(final_path):
            name, ext = os.path.splitext(output_path)
            final_path = f"{name}_{counter}{ext}"
            counter += 1
        
        with open(final_path, 'wb') as f:
            f.write(plaintext)
        
        return {'path': final_path, 'metadata': metadata, 'verified': True}