import binascii
import os.path
import select
import socket
import ssl
import sys
import time
from time import sleep

from Crypto.Cipher import DES

CA_CERT = 'cert/ca.crt'
CLIENT_CERT = 'cert/client.crt'
CLIENT_KEY_FILE = 'cert/client.key'
CERT_PASSWORD = '123456'
SERVER_HOSTNAME = 'hhyserver.com'
HISTORY_KEY = b'12345678'
HISTORY_DIR = 'data/history/'
SERVER_PORT = 7890


def prompt():
    sys.stdout.write('<You(%s) %s> ' % (user,
                                        time.strftime('%Y-%m-%d %H:%M:%S',
                                                      time.localtime(time.time()))))
    sys.stdout.flush()


def save_message(message: str):
    """保存消息到聊天记录"""
    message = message + (8 - len(message) % 8) * ' '  # 八字节对齐
    ciphertext = des_obj.encrypt(message.encode())
    pass_hex = binascii.b2a_hex(ciphertext)
    with open(HISTORY_DIR + user + '.bin', 'ab') as file:
        file.write(pass_hex)


def add_label(msg: str):
    return '\n<' + user + ' ' + \
           time.strftime('%Y-%m-%d %H:%M:%S',
                         time.localtime(time.time())) + '> ' + msg


def retry(msg: str) -> bool:
    ipt = input(msg + ' [y/Else]')
    if ipt == 'y':
        return True
    return False


def sign_in() -> bool:
    print('>>>Sign in OpensslChat\n')
    while True:
        username = input('Username: ')
        password = input('Password: ')
        data = '$SIN$' + username + '\n\n' + password
        ssl_sock.send(data.encode())
        recv = ssl_sock.recv(1024).decode()
        if recv == '$SUC$':
            global user
            user = username
            print('Sign in successfully!')
            sleep(1)
            return True
        else:
            print('Sign in failed! Error: %s' % recv[5:])
            if not retry('Sign in again?'):
                return False


def sign_up():
    print('>>>Sign up to OpensslChat\n')
    while True:
        print("Input following information:")
        username = input('Username: ')
        password = input('Password: ')
        pwd = input('Password(again): ')
        if pwd != password:
            print('The passwords entered in the two times are inconsistent!')
            if not retry('Sign up again?'):
                return
        data = '$SUP$' + username + '\n\n' + password
        ssl_sock.send(data.encode())
        recv = ssl_sock.recv(1024).decode()
        if recv == '$SUC$':
            print('Sign up successfully!')
            sleep(1)
            return
        else:
            print('Sign up failed! Error: %s' % recv[5:])
            if not retry('Sign up again?'):
                return


def running_online():
    print('Connected to OpensslChat. Start sending messages')
    prompt()
    while True:
        read_sockets, _, _ = select.select([sys.stdin, ssl_sock], [], [])
        for sock in read_sockets:
            if sock == ssl_sock:
                data = sock.recv(1024)
                if not data:
                    print('\nDisconnected from chat server')
                    sock.close()
                    return
                else:
                    data = data.decode()[5:]
                    save_message(data)
                    sys.stdout.write(data)
                    prompt()
            else:
                msg = sys.stdin.readline()
                if msg == '!q\n':
                    return
                msg = add_label(msg)
                save_message(msg)
                ssl_sock.send('$MSG$'.encode() + msg.encode())
                prompt()


def exit_prog():
    print('OpensslChat has exited.')
    ssl_sock.close()
    sys.exit()


if __name__ == "__main__":
    hostaddr = '127.0.0.1'
    port = SERVER_PORT

    argc = len(sys.argv)
    if argc > 3:
        print('Usage: python client.py [server_ip] [server_port]')
        sys.exit()
    if argc > 1:
        hostaddr = sys.argv[1]
    if argc > 2:
        port = int(sys.argv[2])

    if not os.path.exists(HISTORY_DIR):
        os.mkdir(HISTORY_DIR)

    des_obj = DES.new(HISTORY_KEY, DES.MODE_ECB)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=CLIENT_CERT, keyfile=CLIENT_KEY_FILE,
                            password=CERT_PASSWORD)
    context.load_verify_locations(CA_CERT)
    ssl_sock = context.wrap_socket(sock, server_hostname=SERVER_HOSTNAME)
    ssl_sock.settimeout(2)

    try:
        ssl_sock.connect((hostaddr, port))
    except Exception as e:
        print(e.args)
        print('Unable to connect!')
        sys.exit()

    user = ''
    print('>>> OpensslChat <<<')
    while True:
        print('\n>>>Menu:\n1. Sign in\n2. Sign up\nElse. Exit')
        ipt = input('Input: ')
        if ipt == '1':
            if sign_in():
                running_online()
                exit_prog()
        elif ipt == '2':
            sign_up()
        else:
            exit_prog()
