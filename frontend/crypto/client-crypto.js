const CryptexClient = {
    SALT_SIZE: 32,
    IV_SIZE: 12,
    KEY_SIZE: 256,
    ITERATIONS: 600000,

    async deriveKey(password, salt) {
        const enc = new TextEncoder();
        const keyMaterial = await crypto.subtle.importKey(
            'raw', enc.encode(password), 'PBKDF2', false, ['deriveBits', 'deriveKey']
        );
        return crypto.subtle.deriveKey(
            { name: 'PBKDF2', salt, iterations: this.ITERATIONS, hash: 'SHA-256' },
            keyMaterial, { name: 'AES-GCM', length: this.KEY_SIZE }, false, ['encrypt', 'decrypt']
        );
    },

    async encryptFile(file, password) {
        const salt = crypto.getRandomValues(new Uint8Array(this.SALT_SIZE));
        const iv = crypto.getRandomValues(new Uint8Array(this.IV_SIZE));
        const key = await this.deriveKey(password, salt);
        const plaintext = await file.arrayBuffer();
        const ciphertext = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, plaintext);
        
        const meta = {
            name: file.name, size: file.size, type: file.type,
            encryptedAt: new Date().toISOString(),
            algorithm: 'AES-256-GCM', kdf: 'PBKDF2-SHA256', iterations: this.ITERATIONS
        };
        const metaBytes = new TextEncoder().encode(JSON.stringify(meta));
        const metaLen = new Uint32Array([metaBytes.length]);
        
        const header = new Uint8Array(this.SALT_SIZE + this.IV_SIZE + 4 + metaBytes.length);
        let o = 0;
        header.set(salt, o); o += this.SALT_SIZE;
        header.set(iv, o); o += this.IV_SIZE;
        header.set(new Uint8Array(metaLen.buffer), o); o += 4;
        header.set(metaBytes, o);
        
        const final = new Uint8Array(header.length + ciphertext.byteLength);
        final.set(header);
        final.set(new Uint8Array(ciphertext), header.length);
        
        return { blob: new Blob([final]), filename: file.name + '.cryptex' };
    },

    async decryptFile(file, password) {
        const data = await file.arrayBuffer();
        const bytes = new Uint8Array(data);
        let o = 0;
        const salt = bytes.slice(o, o + this.SALT_SIZE); o += this.SALT_SIZE;
        const iv = bytes.slice(o, o + this.IV_SIZE); o += this.IV_SIZE;
        const metaLen = new Uint32Array(bytes.slice(o, o + 4).buffer)[0]; o += 4;
        const metaBytes = bytes.slice(o, o + metaLen); o += metaLen;
        const ciphertext = bytes.slice(o);
        const metadata = JSON.parse(new TextDecoder().decode(metaBytes));
        const key = await this.deriveKey(password, salt);
        
        try {
            const plaintext = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext);
            return { blob: new Blob([plaintext], { type: metadata.type }), filename: metadata.name, metadata };
        } catch (e) {
            throw new Error('DECRYPTION FAILED - Wrong password or corrupted file');
        }
    }
};