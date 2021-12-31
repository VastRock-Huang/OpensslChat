import os
import sys
from binascii import a2b_hex

from Crypto.Cipher import DES

MAX_TRY_TIMES = 4
HISTORY_KEY = b'12345678'
HISTORY_DIR = 'data/history/'


print('>>> OpensslChat History <<<')
users = []
for file in os.listdir(HISTORY_DIR):
    if not os.path.isdir(file):
        users.append(file.rstrip('.bin'))
if not users:
    print('No chat history.')
    sys.exit()

username = input('Please input the username: ')
if username not in users:
    print('No chat history of this user.')
    sys.exit()

try_times = 0
while try_times < MAX_TRY_TIMES:
    k = input('Please input the key(8 bytes): ')
    try_times += 1
    if k.encode() == HISTORY_KEY:
        file = open(HISTORY_DIR + username + '.bin', 'rb')
        try:
            text = file.read()
        finally:
            file.close()

        des_obj = DES.new(HISTORY_KEY, DES.MODE_ECB)
        ciphertext = a2b_hex(text)
        plaintext = des_obj.decrypt(ciphertext)
        print('\nChat History:')
        print(plaintext.decode())
        break
    else:
        print(f"Wrong Password! You only have %s trying times!" % (MAX_TRY_TIMES - try_times))
        result = input("Input to try again, or Ctrl+C to quit")
