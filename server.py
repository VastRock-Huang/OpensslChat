import signal
import socket
import select
import ssl
import binascii
from Crypto.Cipher import DES

conn_list = []  # 连接池
RECV_LEN = 1024
PORT = 9999
key = b'12345678'
server_socket = None
des_obj = DES.new(key, DES.MODE_ECB)
# 创建默认SSL上下文
context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain(certfile='./server.crt', keyfile='./server.key',
                        password='123456')


# 数据广播到其它客户端
def broadcast_data(src_sock: ssl.SSLSocket, msg: str):
    # global conn_list
    for sock in conn_list:
        if sock != server_socket and sock != src_sock:
            try:
                sock.write(msg.encode())
            except Exception as e:
                print(e.args)
                sock.close()
                conn_list.remove(sock)


# 保存消息到聊天记录
def save_message(message):
    message = message + (8 - len(message) % 8) * ' '  # 八字节对齐
    ciphertext = des_obj.encrypt(message.encode())
    pass_hex = binascii.b2a_hex(ciphertext)
    with open('data/history.bin', 'ab') as file:
        file.write(pass_hex)


def main():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SOL_SOCKET: 套接字级别设置
    # SO_REUSEADDR: 地址复用
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT))
    # 监听连接,参数为最大未accept的连接数
    server_socket.listen(2)
    conn_list.append(server_socket)
    print("Chat server started on port " + str(PORT))

    conn_map = {}
    while True:
        # 多路复用返回可读连接列表
        read_sockets, _, _ = select.select(conn_list, [], [])
        for sock in read_sockets:
            if sock == server_socket:
                # 返回一个新套接字sockfd,以及另一端套接字绑定的地址addr(hostaddr,post)
                sockfd, addr = server_socket.accept()
                ssl_sock = context.wrap_socket(sockfd, server_side=True)
                conn_list.append(ssl_sock)
                conn_map[ssl_sock] = addr
                print("Client [%s, %s] connected" % addr)
                broadcast_data(ssl_sock, "[%s, %s] entered room\n" % addr)
            else:
                addr, port = conn_map[sock]
                data = sock.read(RECV_LEN)
                if data:
                    message = '\n<%s, %s> %s' % (addr, port, data.decode())
                    # 转发消息给其它用户
                    broadcast_data(sock, message)
                    save_message(message)
                else:
                    broadcast_data(sock, "Client [%s, %s] is offline" % (addr, port))
                    print("Client [%s, %s] is offline" % (addr, port))
                    sock.close()
                    conn_list.remove(sock)


if __name__ == "__main__":
    main()
