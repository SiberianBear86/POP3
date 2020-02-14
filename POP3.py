import socket
import ssl
import re
import base64
import argparse

HOST = 'pop.yandex.ru'
USER = '************'
PASS = '************'
PORT = 995 # 110
EMAIL_PTTRN = re.compile(r'Content-Type: multipart/mixed;\s+boundary="(.*?)"')

def set_socket():
    sock = socket.socket()
    sock.settimeout(1)
    sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
    sock.connect((HOST, PORT))
    print(sock.recv(1024).decode())
    send(sock, "USER {}".format(USER))
    send(sock, "PASS {}".format(PASS))
    print(receive(sock))

    send(sock, "LIST")
    print(receive(sock))

    send(sock, "RETR {}".format(1))
    mail = receive(sock)
    print(mail)
    search = re.search(EMAIL_PTTRN, mail)
    boundary = search.group(1)

    parts = re.split("--{}".format(boundary), mail)
    print(parts)

    text = parts[1]
    text = re.split('\r\n\r\n', text)
    text_headers, text_content = text[0], text[1]
    with open('text.txt', 'w', encoding='utf-8') as f:
        f.write(text_content)

    attachments = parts[2]
    attachments = re.split('\r\n\r\n', attachments)
    att_headers, att_content = attachments[0], attachments[1]
    file_name = re.search('name="(.+?)"', att_headers).group(1)
    with open(file_name, 'wb') as f:
        f.write(base64.b64decode(att_content))
    get_headers(parts[0], sock)

def get_headers(parts, sock):
    parser = argparse.ArgumentParser()
    parser.add_argument("--f", type=str)
    parser.add_argument("--d", type=str)
    parser.add_argument("--t", type=str)
    parser.add_argument("--s", type=str)
    parser.add_argument("--top", type=int)
    d = parser.parse_args()
    headers = [d.f, d.d, d.t, d.s]
    for header in headers:
        if header is not None:
            head = re.search('{}: .*?(?=[\r\n])'.format(header), parts).group(0)
            print('\n' + head)
    if d.top is not None or d.top > 0:
        send(sock, "TOP {} {}".format(1, d.top)) 
        print(receive(sock).split("--")[1])


def send(sock, command):
    sock.sendall("{}\r\n".format(command).encode())


def receive(sock):
    data = b""
    part = b""
    try:
        while True:
            part = sock.recv(1024)
            if not len(part):
                break
            data += part
            part = b""
    except:
        data += part
    return data.decode()


if __name__ == "__main__":
    set_socket()
