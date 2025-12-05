import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def aes_encrypt_file(input_path: str, output_path: str):

    aes_key = AESGCM.generate_key(bit_length=256)
    with open(input_path, "rb") as f:
        plaintext = f.read()
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    with open(output_path, "wb") as f:
        f.write(nonce + ciphertext)

    print(f"[+] Encrypted file saved to: {output_path}")
    print(f"[-] AES key (keep in memory for demo): {aes_key.hex()}")

    return aes_key  
