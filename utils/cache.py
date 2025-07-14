_cache_store = {}

def cache_data(key: str, value):
    """
    Veriyi bellek içi cache'e kaydeder.
    """
    _cache_store[key] = value

def get_cached_data(key: str):
    """
    Cache'te varsa veriyi döner, yoksa None döner.
    """
    return _cache_store.get(key)

def clear_cache():
    """
    Cache'i manuel temizlemek için kullanılır (opsiyonel).
    """
    _cache_store.clear()
