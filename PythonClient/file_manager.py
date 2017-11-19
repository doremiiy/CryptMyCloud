from Crypto.Cipher import AES
from Crypto import Random


def encrypt(in_file, out_file, key):
    with open(in_file, 'rb') as in_file, open(out_file, 'wb') as out_file:
        iv = Random.new().read(AES.block_size)
        out_file.write(iv)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        finished = False
        while not finished:
            chunk = in_file.read(1024 *  AES.block_size)
            if len(chunk) == 0 or len(chunk) % AES.block_size != 0:
                padding_length = ( AES.block_size - len(chunk) %  AES.block_size) or  AES.block_size
                chunk += padding_length * str(padding_length).encode('ascii')
                finished = True
            out_file.write(cipher.encrypt(chunk))


def decrypt(in_file, out_file, key):
    with open(in_file, 'rb') as in_file, open(out_file, 'wb') as out_file:
        iv = in_file.read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        next_chunk = bytes()
        finished = False
        while not finished:
            chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * AES.block_size))
            if len(next_chunk) == 0:
                padding_length = int(chr(chunk[-1]))
                chunk = chunk[:-padding_length]
                finished = True
            out_file.write(chunk)

'''
if __name__ == '__main__':
    import os
    key = os.urandom(32)
    encrypt('test.pdf', 'test2.pdf', key)
    decrypt('test2.pdf', 'test3.pdf', key)
'''