import hashlib

def sanitize_filename(url):
    '''Generate a safe filename from URL using MD5 hash'''
    return hashlib.md5(url.encode('utf-8')).hexdigest()
