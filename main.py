from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

# ====================== 常量定义 ======================
ChToNum = bytes([
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,
    0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09
])

PosOfVin = bytes([0x08,0x07,0x06,0x05,0x04,0x03,0x02,0x0A,0x09,0x08,0x07,0x06,0x05,0x04,0x03,0x02])
key_origin = b"Chery_VIN_To_PIN"

Sbox = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9"
    "ee1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16"
)

Xtime2Sbox = bytes.fromhex(
    "c6f8eef6ffd6de916002ce56e7b54dec8f1f89faefb28efb41b35f452353e49"
    "b75e13d4c6c7ef5836851d1f9e2ab622a0895469d30370a2f0e241bdfcd4e7fe"
    "a121d583436dcb45ba476b77d52dd5e13a6b900c140e379b6d48d67729498b0"
    "85bbc54fed869a66118ae904fea078254ba25d80053f2170f16377af4220e5fd"
    "bf811826c3be35882e9355fc7ac8ba32e6c0199ea344543b0b8cc76b28a7bc16"
    "addb647414920c48b89fbd43c43931d3f2d58b6eda01b19c49d8acf3cfcaf44"
    "7106ff04a5c38577397cba1e83e96610d0fe07c71cc9006f71cc26aae691799"
    "3a27d9eb2b22d2a907332d3c15c987aa50a50359091a65d784d082295a1e7ba86d2c"
)

Xtime3Sbox = bytes.fromhex(
    "a584998d0dbdb1545003a97d1962e69a459d408715ebc90bec67fdeabff7965"
    "bc21cae6a5a41024f5cf434089373533f0c52655e28a10fb509369b3d2669cd"
    "9f1b9e742e2db2eefbf64d61ce7b3e7197f568002c601fc8edbe46d94bded4e"
    "84a6b2ae516c5d75594cf100681f044bae3f3fec08aadbc4804dfc17563301a"
    "0e6d4c14352fe1a2cc3957f28247ace72b95a098d17f667eab83ca29d33c79e"
    "21d763b564e1edb0a6ce45d6eefa6a8a4378b324359b78c64d2e0b4fa0725af"
    "8ee918d5886f7224f1c751237c9c21dddc86859042c4aad8050112a35ff9d091"
    "5827b93813b333bb7089a7b622922049ff787a8ff88017da31c6b8c3b07711cbfcd63a"
)

Rcon = bytes([0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36])

# ====================== 工具函数 ======================
def strbyteget(buf:bytes, idx:int)->int:
    return buf[idx] & 0xFF

def strbyteset(buf:bytearray, idx:int, val:int):
    buf[idx] = val & 0xFF

# ====================== 核心算法 VIN → PIN ======================
def vin_to_pin(vin_str:str)->str:
    vin_str = vin_str.strip().upper()
    if len(vin_str) != 17:
        raise ValueError("VIN长度必须17位")

    temp = vin_str[:8] + vin_str[9:]
    checksum = 0
    plain = bytearray(16)

    for i in range(16):
        c = temp[i]
        if '0' <= c <= '9':
            v = ord(c) - 48
        elif 'A' <= c <= 'Z':
            v = strbyteget(ChToNum, ord(c) - 65)
        else:
            raise ValueError("VIN包含非法字符")
        checksum += v * strbyteget(PosOfVin, i)
        strbyteset(plain, i, ord(c))

    checksum %= 11
    if checksum == 10:
        check_char = 'X'
    else:
        check_char = str(checksum)

    if vin_str[8] != check_char:
        raise ValueError(f"VIN校验位错误，第9位应为 {check_char}")

    # ============ AES密钥扩展 ============
    rk = bytearray(176)
    for i in range(16):
        rk[i] = key_origin[i] if i < 8 else key_origin[i-8]

    for i in range(4, 44):
        a = rk[(i-1)*4]
        b = rk[(i-1)*4+1]
        c = rk[(i-1)*4+2]
        d = rk[(i-1)*4+3]
        if i % 4 == 0:
            a, b, c, d = (
                Sbox[a],
                Sbox[b] ^ Rcon[i//4],
                Sbox[c],
                Sbox[d]
            )
        base = (i-4)*4
        rk[i*4]   = rk[base] ^ a
        rk[i*4+1] = rk[base+1] ^ b
        rk[i*4+2] = rk[base+2] ^ c
        rk[i*4+3] = rk[base+3] ^ d

    # 额外混淆
    tmp3 = 0xA9
    rk[0] ^= tmp3
    tmp0 = 0
    tmp1 = 1
    for idx in range(1, 176):
        v = rk[tmp0] ^ rk[tmp1] ^ tmp3
        rk[idx] = v
        tmp0 = (tmp0 + 1) % 176
        tmp1 = (tmp1 + 1) % 176
        tmp3 = (tmp3 + 41) & 0xFF

    # ============ AES加密 ============
    state = bytearray(16)
    for i in range(16):
        state[i] = plain[i]

    for i in range(16):
        state[i] ^= rk[i]

    for rnd in range(1, 11):
        if rnd < 10:
            ns = bytearray(16)
            s = state
            ns[0]  = Xtime2Sbox[s[0]]  ^ Xtime3Sbox[s[5]] ^ Sbox[s[10]] ^ Sbox[s[15]]
            ns[1]  = Sbox[s[0]]        ^ Xtime2Sbox[s[5]] ^ Xtime3Sbox[s[10]] ^ Sbox[s[15]]
            ns[2]  = Sbox[s[0]]        ^ Sbox[s[5]]       ^ Xtime2Sbox[s[10]] ^ Xtime3Sbox[s[15]]
            ns[3]  = Xtime3Sbox[s[0]]  ^ Sbox[s[5]]       ^ Sbox[s[10]] ^ Xtime2Sbox[s[15]]

            ns[4]  = Xtime2Sbox[s[4]]  ^ Xtime3Sbox[s[9]] ^ Sbox[s[14]] ^ Sbox[s[3]]
            ns[5]  = Sbox[s[4]]        ^ Xtime2Sbox[s[9]] ^ Xtime3Sbox[s[14]] ^ Sbox[s[3]]
            ns[6]  = Sbox[s[4]]        ^ Sbox[s[9]]       ^ Xtime2Sbox[s[14]] ^ Xtime3Sbox[s[3]]
            ns[7]  = Xtime3Sbox[s[4]]  ^ Sbox[s[9]]       ^ Sbox[s[14]] ^ Xtime2Sbox[s[3]]

            ns[8]  = Xtime2Sbox[s[8]]  ^ Xtime3Sbox[s[13]] ^ Sbox[s[2]] ^ Sbox[s[7]]
            ns[9]  = Sbox[s[8]]        ^ Xtime2Sbox[s[13]] ^ Xtime3Sbox[s[2]] ^ Sbox[s[7]]
            ns[10] = Sbox[s[8]]        ^ Sbox[s[13]]       ^ Xtime2Sbox[s[2]] ^ Xtime3Sbox[s[7]]
            ns[11] = Xtime3Sbox[s[8]]  ^ Sbox[s[13]]       ^ Sbox[s[2]] ^ Xtime2Sbox[s[7]]

            ns[12] = Xtime2Sbox[s[12]] ^ Xtime3Sbox[s[1]] ^ Sbox[s[6]] ^ Sbox[s[11]]
            ns[13] = Sbox[s[12]]       ^ Xtime2Sbox[s[1]] ^ Xtime3Sbox[s[6]] ^ Sbox[s[11]]
            ns[14] = Sbox[s[12]]       ^ Sbox[s[1]]       ^ Xtime2Sbox[s[6]] ^ Xtime3Sbox[s[11]]
            ns[15] = Xtime3Sbox[s[12]] ^ Sbox[s[1]]       ^ Sbox[s[6]] ^ Xtime2Sbox[s[11]]
            state = ns
        else:
            s = state[:]
            state = bytearray(16)
            state[0], state[4], state[8], state[12] = Sbox[s[0]], Sbox[s[4]], Sbox[s[8]], Sbox[s[12]]
            state[1], state[5], state[9], state[13] = Sbox[s[5]], Sbox[s[9]], Sbox[s[13]], Sbox[s[1]]
            state[2], state[6], state[10], state[14] = Sbox[s[10]], Sbox[s[14]], Sbox[s[2]], Sbox[s[6]]
            state[3], state[7], state[11], state[15] = Sbox[s[15]], Sbox[s[3]], Sbox[s[7]], Sbox[s[11]]

        for i in range(16):
            state[i] ^= rk[rnd*16 + i]

    pin = ''.join(str(state[i] % 10) for i in range(10))
    if pin[:8] != "00000000":
        return pin[:8]
    else:
        return pin[-8:]

# ====================== Kivy UI ======================
KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 15

    Label:
        text: '奇瑞 VIN → PIN'
        font_size: '24sp'
        size_hint_y: None
        height: '50dp'

    TextInput:
        id: vin
        hint_text: '输入17位VIN码'
        multiline: False
        font_size: '18sp'

    Button:
        text: '计算 PIN 码'
        font_size: '18sp'
        on_press: app.calc()

    Label:
        id: result
        text: ''
        font_size: '22sp'
        color: 0,1,0,1
'''

class VINApp(App):
    def build(self):
        return Builder.load_string(KV)

    def calc(self):
        try:
            pin = vin_to_pin(self.root.ids.vin.text)
            self.root.ids.result.text = f"PIN：{pin}"
        except Exception as e:
            self.root.ids.result.text = f"错误：{e}"

if __name__ == '__main__':
    VINApp().run()
