import selectors
import socket, select, string, sys, ssl


def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()


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

    while True:
        read_sockets, write_sockets, error_sockets = select.select([sys.stdin, ssl_sock], [], [])
        for sock in read_sockets:
            if sock == ssl_sock:
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from chat server')
                    sock.close()
                    return
                else:
                    sys.stdout.write(data.decode())
                    prompt()
            else:
                msg = sys.stdin.readline()
                if msg == 'quit':
                    sock.close()
                    return
                ssl_sock.send(msg.encode())
                prompt()


if __name__ == "__main__":
    main()
