import socket

BUF_SIZE = 8192

listen_addr = ("0.0.0.0", 11111)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(listen_addr)

addrs = {
    "192.168.0.11": ("127.0.0.1", 12000),
}

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    data, (ip, port) = s.recvfrom(BUF_SIZE)
    if ip in addrs:
        c.sendto(data, addrs[ip])