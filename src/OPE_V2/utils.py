import hashlib
from typing import Iterable, Optional

def hash_concat(strings: Iterable[str], sep: str = "", algorithm: str = "sha256", encoding: str = "utf-8") -> str:
    """
    Concatène les chaînes de `strings` avec `sep` puis retourne le hash hexadécimal selon `algorithm`.
    algorithm: "sha256", "sha1", "md5", etc. (préférer sha256)
    """
    # Concaténation
    concat = sep.join(strings)
    # Calcul du hash
    h = hashlib.new(algorithm)
    h.update(concat.encode(encoding))
    return h.hexdigest()