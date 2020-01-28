import hashlib


def get_uiid(identifier):
    print("Calling get_uiid")
    t_value = identifier.encode('utf8')
    h = hashlib.sha256(t_value)
    n = int(h.hexdigest(), base=16)
    print(n)