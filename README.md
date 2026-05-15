# 🔐 CRYPTEX XDR

![Zero-Knowledge](https://img.shields.io/badge/Zero--Knowledge-True-green)
![AES-256-GCM](https://img.shields.io/badge/Encryption-AES--256--GCM-blue)
![Web Crypto API](https://img.shields.io/badge/API-Web%20Crypto-orange)
![Python](https://img.shields.io/badge/Backend-FastAPI-009688)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Zero-Knowledge Secure File Vault with Client-Side Encryption**

---

## 🔒 Security Model

CRYPTEX XDR uses **true zero-knowledge architecture**:

- ✅ Encryption happens **entirely in your browser** (Web Crypto API)
- ✅ Passwords **never leave your device**
- ✅ Plaintext **never touches the server**
- ✅ Backend stores only **encrypted blobs**
- ✅ AES-256-GCM authenticated encryption
- ✅ PBKDF2 key derivation (600,000 iterations)

---

## ⚡ Features

### 🔐 Core Encryption
- Client-side AES-256-GCM encryption
- PBKDF2-HMAC-SHA256 key derivation
- Per-file random salt & IV
- Authenticated encryption (tamper detection)
- Custom `.cryptex` secure container format

### 📁 Secure Vault
- Encrypted file storage
- Vault file explorer
- Drag & drop upload
- Download encrypted files
- Storage analytics

### 🛡️ Security
- 7-pass secure file shredder
- Complete audit logging
- Password strength analyzer
- Wrong password detection
- Tamper verification
- Session monitoring

### 🎨 Interface
- Premium dark UI (Emerald Vault theme)
- Real-time statistics
- Activity log
- Password strength meter
- Responsive design

---

## 🏗️ Architecture
