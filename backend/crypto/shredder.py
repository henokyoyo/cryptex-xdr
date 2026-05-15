import os, random

class SecureShredder:
    @staticmethod
    def shred(filepath: str, passes: int = 7) -> bool:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        size = os.path.getsize(filepath)
        
        for p in range(passes):
            with open(filepath, 'wb') as f:
                if p == passes - 1:
                    f.write(b'\x00' * size)
                else:
                    chunk_size = min(size, 1048576)
                    f.write(bytes([random.randint(0, 255) for _ in range(chunk_size)]))
                    f.seek(0)
                    f.write(os.urandom(size))
        
        os.remove(filepath)
        return True