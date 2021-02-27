import config

def loader(key, default=None):
    if hasattr(config, key):
        return getattr(config, key)
    return default