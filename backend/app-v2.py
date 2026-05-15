"""
CRYPTEX XDR v2.0 - Zero-Knowledge Secure File Vault
TRUE Client-Side Encryption - Backend NEVER sees passwords or plaintext
"""

from fastapi import FastAPI, UploadFile, File, Form, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, json, shutil
from datetime import datetime

app = FastAPI(title="CRYPTEX XDR v2.0", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

os.makedirs("uploads", exist_ok=True)
os.makedirs("vault", exist_ok=True)
os.makedirs("audit", exist_ok=True)

active_ws = []
stats = {"files_stored": 0, "total_bytes": 0, "vault_size": 0}

# ========== STATIC FILES ==========
@app.get("/static/client-crypto.js")
async def crypto_js():
    path = os.path.join("frontend", "crypto", "client-crypto.js")
    return FileResponse(path, media_type="application/javascript")

# ========== VAULT PAGE ==========
@app.get("/", response_class=HTMLResponse)
async def vault_v2():
    path = os.path.join("frontend", "pages", "vault-v2.html")
    if os.path.exists(path): return open(path, encoding="utf-8").read()
    return "<h1>CRYPTEX XDR v2.0</h1>"

# ========== STORE ENCRYPTED BLOB (NEVER sees plaintext) ==========
@app.post("/api/vault/store")
async def store_encrypted(file: UploadFile = File(...)):
    """Store already-encrypted blob. Backend NEVER decrypts."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{file.filename}"
    filepath = os.path.join("vault", safe_name)
    
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    stats["files_stored"] += 1
    stats["total_bytes"] += os.path.getsize(filepath)
    stats["vault_size"] = sum(os.path.getsize(os.path.join("vault", f)) for f in os.listdir("vault") if os.path.isfile(os.path.join("vault", f)))
    
    _audit_log("VAULT_STORE", {"file": safe_name, "size": os.path.getsize(filepath)})
    await _broadcast({"type": "vault_update", "stats": stats})
    
    return {"status": "stored", "filename": safe_name, "vault_size": stats["vault_size"]}

# ========== LIST VAULT FILES ==========
@app.get("/api/vault/list")
async def list_vault():
    files = []
    for f in os.listdir("vault"):
        fp = os.path.join("vault", f)
        if os.path.isfile(fp):
            files.append({"name": f, "size": os.path.getsize(fp), "stored_at": datetime.fromtimestamp(os.path.getmtime(fp)).isoformat()})
    return sorted(files, key=lambda x: x["stored_at"], reverse=True)

# ========== DOWNLOAD FROM VAULT ==========
@app.get("/api/vault/download/{filename}")
async def download_vault(filename: str):
    fp = os.path.join("vault", filename)
    if os.path.exists(fp):
        _audit_log("VAULT_DOWNLOAD", {"file": filename})
        return FileResponse(fp, filename=filename)
    return JSONResponse({"error": "Not found"}, 404)

# ========== SHRED FROM VAULT ==========
@app.delete("/api/vault/shred/{filename}")
async def shred_vault(filename: str):
    fp = os.path.join("vault", filename)
    if os.path.exists(fp):
        import random
        size = os.path.getsize(fp)
        for _ in range(7):
            with open(fp, 'wb') as f:
                f.write(os.urandom(min(size, 1048576)))
        os.remove(fp)
        _audit_log("VAULT_SHRED", {"file": filename})
        await _broadcast({"type": "vault_update"})
        return {"status": "shredded"}
    return JSONResponse({"error": "Not found"}, 404)

# ========== STATS ==========
@app.get("/api/stats")
async def get_stats():
    stats["vault_size"] = sum(os.path.getsize(os.path.join("vault", f)) for f in os.listdir("vault") if os.path.isfile(os.path.join("vault", f)))
    return stats

# ========== AUDIT ==========
@app.get("/api/audit")
async def get_audit(limit: int = 50):
    fp = "audit/audit_log.json"
    if not os.path.exists(fp): return []
    with open(fp) as f:
        try: return json.load(f)[-limit:]
        except: return []

def _audit_log(event, details):
    os.makedirs("audit", exist_ok=True)
    fp = "audit/audit_log.json"
    logs = []
    if os.path.exists(fp):
        with open(fp) as f:
            try: logs = json.load(f)
            except: logs = []
    logs.append({"timestamp": datetime.now().isoformat(), "event": event, "details": details})
    with open(fp, "w") as f: json.dump(logs[-500:], f, indent=2)

# ========== WEBSOCKET ==========
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_ws.append(websocket)
    try:
        while True: await websocket.receive_text()
    except:
        if websocket in active_ws: active_ws.remove(websocket)

async def _broadcast(data):
    for ws in active_ws:
        try: await ws.send_json(data)
        except: active_ws.remove(ws)

# ========== START ==========
if __name__ == "__main__":
    import uvicorn
    print("""
╔══════════════════════════════════════════════╗
║     🔐 CRYPTEX XDR v2.0 - ZERO KNOWLEDGE    ║
║   Client-Side Encryption · Web Crypto API    ║
╠══════════════════════════════════════════════╣
║  🏠 Vault:  http://localhost:8000            ║
║  📡 WS:     ws://localhost:8000/ws           ║
╚══════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)