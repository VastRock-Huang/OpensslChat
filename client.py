import selectors
import socket
import ssl
import sys

running = True

def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


def recv_sock(sock, mask, arg):
    data = sock.recv(4096)
    if not data:
        print('\nDisconnected from chat server')
        sock.close()
        global running
        running = False
        return
    else:
        sys.stdout.write(data)
        prompt()

def input_msg(stdin, mask, ssl_sock):
    msg = sys.stdin.readline()
    if msg == 'quit':
        ssl_sock.close()
        global running
        running = False
        return
    ssl_sock.send(msg)
    prompt()

def main():
    if len(sys.argv) < 3:
        print('Usage : python chat_client.py hostname port')
        return

    hostaddr = sys.argv[1]
    port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_verify_locations('ca.crt')
    ssl_sock = context.wrap_socket(sock, server_hostname='hhyserver.com')
    ssl_sock.settimeout(2)

    try:
        ssl_sock.connect((hostaddr, port))
    except Exception as e:
        print(e.args)
        print('Unable to connect!')
        return

    print('Connected to remote host. Start sending messages')
    prompt()

    sel = selectors.DefaultSelector()
    sel.register(ssl_sock, selectors.EVENT_READ, [recv_sock])
    sel.register(sys.stdin, selectors.EVENT_READ, [input_msg, ssl_sock])

    while running:
        for key, mask in sel.select():
            callback = key.data[0]
            callback(key.fileobj, mask, key.data[1])


if __name__ == "__main__":
    main()
