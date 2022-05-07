import hashlib
import random
import string

def hash_str(s): 
  #return the hashdigest created byhashlib's md5 hash of str(s).encode("utf-8")
  for i in range(100):
    s = hashlib.md5(str(s).encode("utf-8")).hexdigest()
  return s[:4]+"".join(random.choices(string.ascii_letters+string.digits, k=10))+s[4:]

# Take the string with  visits and the hash and return the confirmed results.
def check_secure_val(s, hash, salt):
    hash = hash[:4]+hash[14:]
    # return s if the hash_str(s) equals hash, otherwise return None
    s = hash_str(s+salt)
    if s[:4]+s[14:] == hash:
      return True
    else:
      return None