import hashlib

def sanitize_filename(url: str) -> str:
    '''
    Generate a safe filename from a URL by hashing it with MD5.

    Args:
        url: The URL string to be sanitized.

    Returns:
        The MD5 hash of the URL as a hexadecimal string, which is used as a safe filename.
    '''
    return hashlib.md5(url.encode('utf-8')).hexdigest()
