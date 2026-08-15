# ====================== 常量定义 ======================
ChToNum = bytes([
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,
    0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09
])

PosOfVin = bytes([0x08,0x07,0x06,0x05,0x04,0x03,0x02,0x0A,0x09,0x08,0x07,0x06,0x05,0x04,0x03,0x02])

_key_parts = [b"Chery_", b"VIN_", b"To_", b"PIN"]
key_origin = b"".join(_key_parts)

Sbox_hex = ("637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0b7fd9326363ff7cc34a5e5f171d8311504c7"
            "23c31896059a071280e2eb27b27509832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cfd0efaafb"
            "434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2cd0c13ec5f974417c4a77e3d645d197360814fdc222a"
            "908846eeb814de5e0bdbe0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08ba78252e1ca6b4c6"
            "e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9ee1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")
Sbox = bytes.fromhex(Sbox_hex)

Xtime2Sbox_hex = ("c6f8eef6ffd6de916002ce56e7b54dec8f1f89faefb28efb41b35f452353e49b75e13d4c6c7ef5836851d1f9e2ab62"
                  "2a0895469d30370a2f0e241bdfcd4e7fea121d583436dcb45ba476b77d52dd5e13a6b900c140e379b6d48d67729498"
                  "b085bbc54fed869a66118ae904fea078254ba25d80053f2170f16377af4220e5fdbf811826c3be35882e9355fc7ac8"
                  "ba32e6c0199ea344543b0b8cc76b28a7bc16addb647414920c48b89fbd43c43931d3f2d58b6eda01b19c49d8acf3cf"
                  "caf447106ff04a5c38577397cba1e83e96610d0fe07c71cc9006f71cc26aae6917993a27d9eb2b22d2a907332d3c15"
                  "c987aa50a50359091a65d784d082295a1eb86d2c")
Xtime2Sbox = bytes.fromhex(Xtime2Sbox_hex)

Xtime3Sbox_hex = ("a584998d0dbdb1545003a97d1962e69a459d408715ebc90bec67fdeabff7965bc21cae6a5a41024f5cf43408937353"
                  "3f0c52655e28a10fb509369b3d2669cd9f1b9e742e2db2eefbf64d61ce7b3e7197f568002c601fc8edbe46d94bded4"
                  "e84a6b2ae516c5d75594cf100681f044bae3f3fec08aadbc4804dfc17563301a0e6d4c14352fe1a2cc3957f28247ac"
                  "e72b95a098d17f667eab83ca29d33c79e21d763b564e1edb0a6ce45d6eefa6a8a4378b324359b78c64d2e0b4fa0725"
                  "af8ee918d5886f7224f1c751237c9c21dddc86859042c4aad8050112a35ff9d0915827b93813b333bb7089a7b62292"
                  "2049ff787a8ff88017da31c6b8c3b07711cbfcd63a")
Xtime3Sbox = bytes.fromhex(Xtime3Sbox_hex)

Rcon = bytes([0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36])

# ====================== 工具函数 ======================
def _get(buf, idx):
    return buf[idx] & 0xFF

def _set(buf, idx, val):
    buf[idx] = val & 0xFF

def _mid(s, start, length):
    return s[start:start+length]

def _right(s, n):
    return s[-n:] if n > 0 else ""

def _upr(s):
    return s.upper()

# ====================== 核心：VIN -> PIN ======================
def vin_to_pin(vin_str: str) -> str:
    vin_str = vin_str.strip()
    if len(vin_str) != 17:
        raise Exception("VIN长度必须17位！")
    VIN_T = _upr(vin_str)

    Temp = _mid(VIN_T, 0, 8) + _right(VIN_T, 8)
    CheckSum = 0
    PlainVin = bytearray(16)

    for i in range(16):
        c = Temp[i]
        if '0' <= c <= '9':
            val = ord(c) - 48
            CheckSum += val * _get(PosOfVin, i)
        elif 'A' <= c <= 'Z':
            idx_ch = ord(c) - 65
            v = _get(ChToNum, idx_ch)
            CheckSum += v * _get(PosOfVin, i)
        _set(PlainVin, i, ord(c))

    CheckSum = CheckSum % 11
    tp = str(CheckSum)
    vin_check_char = VIN_T[8]
    valid = False
    if tp == vin_check_char:
        valid = True
    elif tp == "10" and vin_check_char == 'X':
        valid = True
    if not valid:
        raise Exception(f"VIN校验位错误！第9位[{vin_check_char}]，计算值={CheckSum}")

    # ---------- AES 密钥扩展 ----------
    RoundKey = bytearray(176)
    kb = key_origin
    idx = 0
    while idx < 16:
        if idx < 8:
            _set(RoundKey, idx, _get(kb, idx))
        else:
            _set(RoundKey, idx, _get(kb, idx - 8))
        idx += 1

    idx = 4
    while idx < 44:
        w0 = _get(RoundKey, idx*4-4)
        w1 = _get(RoundKey, idx*4-3)
        w2 = _get(RoundKey, idx*4-2)
        w3 = _get(RoundKey, idx*4-1)
        t0, t1, t2, t3 = w0, w1, w2, w3
        if (idx % 4) == 0:
            tmp4 = t3
            t3 = _get(Sbox, t0)
            t0 = _get(Sbox, t1) ^ _get(Rcon, idx//4)
            t1 = _get(Sbox, t2)
            t2 = _get(Sbox, tmp4)
        _set(RoundKey, idx*4+0, _get(RoundKey, (idx-4)*4+0) ^ t0)
        _set(RoundKey, idx*4+1, _get(RoundKey, (idx-4)*4+1) ^ t1)
        _set(RoundKey, idx*4+2, _get(RoundKey, (idx-4)*4+2) ^ t2)
        _set(RoundKey, idx*4+3, _get(RoundKey, (idx-4)*4+3) ^ t3)
        idx += 1

    # 混淆
    _set(RoundKey, 0, _get(RoundKey, 0) ^ 0xA9)
    idx = 1; tmp0 = 0; tmp1 = 1; tmp3 = 0xA9
    while idx < 176:
        v = _get(RoundKey, tmp0) ^ _get(RoundKey, tmp1) ^ tmp3
        _set(RoundKey, idx, v)
        tmp0 = (tmp0 + 1) % 176
        tmp1 = (tmp1 + 1) % 176
        tmp3 = (tmp3 + 41) & 0xFF
        idx += 1

    # ---------- AES 加密 ----------
    state = bytearray(16)
    for i in range(16):
        _set(state, i, _get(PlainVin, i))

    for i in range(16):
        _set(state, i, state[i] ^ _get(RoundKey, i))

    round = 1
    while round < 11:
        if round < 10:
            s = state
            ns = bytearray(16)
            _set(ns,0, _get(Xtime2Sbox,s[0]) ^ _get(Xtime3Sbox,s[5]) ^ _get(Sbox,s[10]) ^ _get(Sbox,s[15]))
            _set(ns,1, _get(Sbox,s[0]) ^ _get(Xtime2Sbox,s[5]) ^ _get(Xtime3Sbox,s[10]) ^ _get(Sbox,s[15]))
            _set(ns,2, _get(Sbox,s[0]) ^ _get(Sbox,s[5]) ^ _get(Xtime2Sbox,s[10]) ^ _get(Xtime3Sbox,s[15]))
            _set(ns,3, _get(Xtime3Sbox,s[0]) ^ _get(Sbox,s[5]) ^ _get(Sbox,s[10]) ^ _get(Xtime2Sbox,s[15]))
            _set(ns,4, _get(Xtime2Sbox,s[4]) ^ _get(Xtime3Sbox,s[9]) ^ _get(Sbox,s[14]) ^ _get(Sbox,s[3]))
            _set(ns,5, _get(Sbox,s[4]) ^ _get(Xtime2Sbox,s[9]) ^ _get(Xtime3Sbox,s[14]) ^ _get(Sbox,s[3]))
            _set(ns,6, _get(Sbox,s[4]) ^ _get(Sbox,s[9]) ^ _get(Xtime2Sbox,s[14]) ^ _get(Xtime3Sbox,s[3]))
            _set(ns,7, _get(Xtime3Sbox,s[4]) ^ _get(Sbox,s[9]) ^ _get(Sbox,s[14]) ^ _get(Xtime2Sbox,s[3]))
            _set(ns,8, _get(Xtime2Sbox,s[8]) ^ _get(Xtime3Sbox,s[13]) ^ _get(Sbox,s[2]) ^ _get(Sbox,s[7]))
            _set(ns,9, _get(Sbox,s[8]) ^ _get(Xtime2Sbox,s[13]) ^ _get(Xtime3Sbox,s[2]) ^ _get(Sbox,s[7]))
            _set(ns,10, _get(Sbox,s[8]) ^ _get(Sbox,s[13]) ^ _get(Xtime2Sbox,s[2]) ^ _get(Xtime3Sbox,s[7]))
            _set(ns,11, _get(Xtime3Sbox,s[8]) ^ _get(Sbox,s[13]) ^ _get(Sbox,s[2]) ^ _get(Xtime2Sbox,s[7]))
            _set(ns,12, _get(Xtime2Sbox,s[12]) ^ _get(Xtime3Sbox,s[1]) ^ _get(Sbox,s[6]) ^ _get(Sbox,s[11]))
            _set(ns,13, _get(Sbox,s[12]) ^ _get(Xtime2Sbox,s[1]) ^ _get(Xtime3Sbox,s[6]) ^ _get(Sbox,s[11]))
            _set(ns,14, _get(Sbox,s[12]) ^ _get(Sbox,s[1]) ^ _get(Xtime2Sbox,s[6]) ^ _get(Xtime3Sbox,s[11]))
            _set(ns,15, _get(Xtime3Sbox,s[12]) ^ _get(Sbox,s[1]) ^ _get(Sbox,s[6]) ^ _get(Xtime2Sbox,s[11]))
            state = ns
        else:
            s = state.copy()
            _set(state,0, _get(Sbox,s[0]))
            _set(state,4, _get(Sbox,s[4]))
            _set(state,8, _get(Sbox,s[8]))
            _set(state,12, _get(Sbox,s[12]))
            t = _get(Sbox,s[1])
            _set(state,1, _get(Sbox,s[5])); _set(state,5, _get(Sbox,s[9]))
            _set(state,9, _get(Sbox,s[13])); _set(state,13, t)
            t = _get(Sbox,s[2])
            _set(state,2, _get(Sbox,s[10])); _set(state,10, t)
            t = _get(Sbox,s[6])
            _set(state,6, _get(Sbox,s[14])); _set(state,14, t)
            t = _get(Sbox,s[15])
            _set(state,15, _get(Sbox,s[11])); _set(state,11, _get(Sbox,s[7]))
            _set(state,7, _get(Sbox,s[3])); _set(state,3, t)

        koff = round * 16
        for i in range(16):
            _set(state, i, state[i] ^ _get(RoundKey, koff + i))
        round += 1

    PinStr = ""
    for i in range(10):
        PinStr += str(state[i] % 10)
    if _mid(PinStr, 0, 8) != "00000000":
        return _mid(PinStr, 0, 8)
    return _right(PinStr, 8)
