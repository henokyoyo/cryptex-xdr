from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, HMAC
import os, struct, json
from datetime import datetime

class CryptexEncryptor:
    SALT_SIZE = 32
    NONCE_SIZE = 12
    ITERATIONS = 600000

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        return PBKDF2(password.encode(), salt, dkLen=32, count=600000, hmac_hash_module=SHA256)

    @staticmethod
    def encrypt_file(filepath: str, password: str, metadata: dict = None) -> str:
        salt = get_random_bytes(32)
        nonce = get_random_bytes(12)
        key = CryptexEncryptor.derive_key(password, salt)
        
        with open(filepath, 'rb') as f:
            plaintext = f.read()
        
        original_hash = SHA256.new(plaintext).hexdigest()
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        
        meta = metadata or {}
        meta['original_filename'] = os.path.basename(filepath)
        meta['original_size'] = len(plaintext)
        meta['original_hash'] = original_hash
        meta['encrypted_at'] = datetime.now().isoformat()
        meta['algorithm'] = 'AES-256-GCM'
        meta['kdf'] = 'PBKDF2-HMAC-SHA256'
        meta['iterations'] = 600000
        meta_bytes = json.dumps(meta).encode()
        meta_len = struct.pack('<I', len(meta_bytes))
        
        header = salt + nonce + meta_len + meta_bytes
        hmac = HMAC.new(key, header + ciphertext, SHA256).digest()
        
        output_path = filepath + '.cryptex'
        with open(output_path, 'wb') as f:
            f.write(header + tag + hmac + ciphertext)
        
        return output_path