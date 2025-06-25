import hashlib

predefined_string = "erica1234"

def url_converter(value: str) -> str:
    hash_object = hashlib.md5()
    hash_object.update(value.encode())
    return hash_object.hexdigest()[:7]


    