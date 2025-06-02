# sm3.py

import struct

# Constants
IV = [
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
]

T_j = [0]*64
for i in range(16):
    T_j[i] = 0x79CC4519
for i in range(16, 64):
    T_j[i] = 0x7A879D8A

def _rotate_left(x, n):
    n = n % 32 
    return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))


def _ff_j(x, y, z, j):
    if j >= 0 and j <= 15:
        return x ^ y ^ z
    else:
        return (x & y) | (x & z) | (y & z)

def _gg_j(x, y, z, j):
    if j >= 0 and j <= 15:
        return x ^ y ^ z
    else:
        return (x & y) | ((~x) & z)

def _p0(x):
    return x ^ _rotate_left(x, 9) ^ _rotate_left(x, 17)

def _p1(x):
    return x ^ _rotate_left(x, 15) ^ _rotate_left(x, 23)

def _cf(v_i, b_i):
    """
    Compression function
    :param v_i: The vector from the previous iteration (8x32 bits)
    :param b_i: The current 512-bit block, converted to 16x32-bit words
    :return: The vector from the current iteration (8x32 bits)
    """
    w = [0]*68
    w_1 = [0]*64

    for i in range(16):
        w[i] = b_i[i]
    for i in range(16, 68):
        w[i] = _p1(w[i-16] ^ w[i-9] ^ _rotate_left(w[i-3], 15)) ^ _rotate_left(w[i-13], 7) ^ w[i-6]
    for i in range(64):
        w_1[i] = w[i] ^ w[i+4]

    A, B, C, D, E, F, G, H = v_i

    for i in range(64):
        ss1 = _rotate_left(((A & 0xFFFFFFFF) + (E & 0xFFFFFFFF) + _rotate_left(T_j[i], i) ) & 0xFFFFFFFF, 7)
        ss2 = ss1 ^ _rotate_left(A, 12)
        tt1 = (_ff_j(A, B, C, i) + D + ss2 + w_1[i]) & 0xFFFFFFFF
        tt2 = (_gg_j(E, F, G, i) + H + ss1 + w[i]) & 0xFFFFFFFF
        D = C
        C = _rotate_left(B, 9)
        B = A
        A = tt1
        H = G
        G = _rotate_left(F, 19)
        F = E
        E = _p0(tt2)

    return [A ^ v_i[0], B ^ v_i[1], C ^ v_i[2], D ^ v_i[3],
            E ^ v_i[4], F ^ v_i[5], G ^ v_i[6], H ^ v_i[7]]

def sm3_hash(data: bytes) -> str:
    """
    The SM3 hash function hashes the data and returns a hexadecimal string.
    """
    # Convert to bit length
    length = len(data)
    reserve1 = length << 3

    # Padding
    data += b'\x80'
    remainder = len(data) % 64
    padding = (56 - remainder) if remainder < 56 else (120 - remainder)
    data += b'\x00' * padding
    data += struct.pack('>Q', reserve1)

    # Group by 512 bits (64 bytes)
    group_count = len(data) // 64

    V = IV[:]
    for i in range(group_count):
        block = data[i*64:(i+1)*64]
        B = []
        for j in range(16):
            B.append(struct.unpack('>I', block[j*4:(j+1)*4])[0])
        V = _cf(V, B)

    return ''.join(['%08x' % i for i in V])
