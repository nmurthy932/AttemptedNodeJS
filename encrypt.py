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

def encryptEmail(email):
  return hashlib.md5(str(email).encode("utf-8")).hexdigest()

def encryptRole(role):
  return hashlib.md5(str(role).encode("utf-8")).hexdigest()

def check_email(encrypted):
  encrypted = encrypted.split('|')
  if len(encrypted) > 1:
    email = encrypted[0]
    hash = encrypted [1]
    if encryptEmail(email) == hash:
      return True
  else:
    return False

def check_role(encrypted):
  encrypted = encrypted.split('|')
  if len(encrypted) > 1:
    email = encrypted[0]
    hash = encrypted[1]
    role = encrypted[2]
    roleHash = encrypted[3]
    if encryptRole(role) == roleHash and role == 'teacher':
      return True
  else:
    return False