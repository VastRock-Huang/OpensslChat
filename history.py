from binascii import a2b_hex

from Crypto.Cipher import DES

import config

MAX_TRY_TIMES = 4

try_times = 0
while try_times < MAX_TRY_TIMES:
    k = input('Please input the key(8 bytes): ')
    try_times += 1
    if k == config.HISTORY_KEY:
        file = open(config.HISTORY_FILE, 'rb')
        try:
            text = file.read()
        finally:
            file.close()

        des_obj = DES.new(k.encode(), DES.MODE_ECB)
        ciphertext = a2b_hex(text)
        plaintext = des_obj.decrypt(ciphertext)
        print('\nChat History:')
        print(plaintext.decode())
        break
    else:
        print(f"Wrong Password! You only have {MAX_TRY_TIMES - try_times} trying times!")
        result = input("Input to try again, or Ctrl+C to quit")
