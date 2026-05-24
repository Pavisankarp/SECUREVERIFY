import hashlib

def generate_hash(file):
    """Generates a SHA-256 hash of the file content in chunks."""
    sha256 = hashlib.sha256()
    while True:
        chunk = file.read(4096)
        if not chunk:
            break
        sha256.update(chunk)
    file.seek(0)  # Reset pointer
    return sha256.hexdigest()