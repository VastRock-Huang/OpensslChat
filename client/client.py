import binascii
import select
import socket
import ssl
import sys

from Crypto.Cipher import DES

CA_CERT = 'cert/ca.crt'
SERVER_HOSTNAME = 'hhyserver.com'
HISTORY_KEY = b'123456'
HISTORY_FILE = 'data/history.bin'
SERVER_PORT = 7890

des_obj = DES.new(HISTORY_KEY, DES.MODE_ECB)


def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


# 保存消息到聊天记录
def save_message(message: str):
    message = message + (8 - len(message) % 8) * ' '  # 八字节对齐
    ciphertext = des_obj.encrypt(message.encode())
    pass_hex = binascii.b2a_hex(ciphertext)
    with open(HISTORY_FILE, 'ab') as file:
        file.write(pass_hex)


def main():
    hostaddr = '127.0.0.1'
    port = SERVER_PORT

    argc = len(sys.argv)
    if argc > 3:
        print('Usage: python client.py [server_ip] [server_port]')
        return
    if argc > 1:
        hostaddr = sys.argv[1]
    if argc > 2:
        port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_verify_locations(CA_CERT)
    ssl_sock = context.wrap_socket(sock, server_hostname=SERVER_HOSTNAME)
    ssl_sock.settimeout(2)

    try:
        ssl_sock.connect((hostaddr, port))
    except Exception as e:
        print(e.args)
        print('Unable to connect!')
        return

    print('Connected to remote host. Start sending messages')
    prompt()

    while True:
        read_sockets, write_sockets, error_sockets = select.select([sys.stdin, ssl_sock], [], [])
        for sock in read_sockets:
            if sock == ssl_sock:
                data = sock.recv(1024)
                if not data:
                    print('\nDisconnected from chat server')
                    sock.close()
                    return
                else:
                    save_message(data.decode())
                    sys.stdout.write(data.decode())
                    prompt()
            else:
                msg = sys.stdin.readline()
                if msg == '!q':
                    sock.close()
                    return
                save_message(msg)
                ssl_sock.send(msg.encode())
                prompt()


if __name__ == "__main__":
    main()
