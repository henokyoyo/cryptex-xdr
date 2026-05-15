import re, os

class Validators:
    MAX_FILE_SIZE = 500 * 1024 * 1024

    @staticmethod
    def validate_password(password: str) -> dict:
        result = {'valid': False, 'score': 0, 'feedback': [], 'level': 'Weak'}
        
        if len(password) >= 8: result['score'] += 20
        else: result['feedback'].append('At least 8 characters')
        
        if re.search(r'[A-Z]', password): result['score'] += 20
        else: result['feedback'].append('Add uppercase letter')
        
        if re.search(r'[a-z]', password): result['score'] += 20
        else: result['feedback'].append('Add lowercase letter')
        
        if re.search(r'\d', password): result['score'] += 20
        else: result['feedback'].append('Add number')
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): result['score'] += 20
        else: result['feedback'].append('Add special character')
        
        result['valid'] = result['score'] >= 60
        if result['score'] >= 80: result['level'] = 'Strong'
        elif result['score'] >= 40: result['level'] = 'Medium'
        
        chars = len(set(password))
        result['crack_time'] = f"{pow(chars, len(password)) // 1000000000:,} years" if result['score'] >= 60 else "Instantly"
        
        return result

    @staticmethod
    def validate_file(filepath: str) -> dict:
        if not os.path.exists(filepath):
            return {'valid': False, 'error': 'File not found'}
        size = os.path.getsize(filepath)
        if size > Validators.MAX_FILE_SIZE:
            return {'valid': False, 'error': f'File too large. Max 500MB'}
        return {'valid': True, 'size': size, 'name': os.path.basename(filepath)}