# ====================== 常量定义(和原始代码完全对齐) ======================
ChToNum = bytes([
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,
    0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,
    0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09
])

PosOfVin = bytes([0x08,0x07,0x06,0x05,0x04,0x03,0x02,0x0A,0x09,0x08,0x07,0x06,0x05,0x04,0x03,0x02])

key_origin = b"Chery_VIN_To_PIN"  # 原始密钥字符串

# Sbox 原始十六进制串
Sbox_hex = "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0b7fd9326363ff7cc34a5e5f171d8311504c7" \
           "23c31896059a071280e2eb27b27509832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cfd0efaafb" \
           "434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2cd0c13ec5f974417c4a77e3d645d197360814fdc222a" \
           "908846eeb814de5e0bdbe0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08ba78252e1ca6b4c6" \
           "e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9ee1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16"
Sbox = bytes.fromhex(Sbox_hex)

Xtime2Sbox_hex = "c6f8eef6ffd6de916002ce56e7b54dec8f1f89faefb28efb41b35f452353e49b75e13d4c6c7ef5836851d1f9e2ab62" \
                 "2a0895469d30370a2f0e241bdfcd4e7fea121d583436dcb45ba476b77d52dd5e13a6b900c140e379b6d48d67729498" \
                 "b085bbc54fed869a66118ae904fea078254ba25d80053f2170f16377af4220e5fdbf811826c3be35882e9355fc7ac8" \
                 "ba32e6c0199ea344543b0b8cc76b28a7bc16addb647414920c48b89fbd43c43931d3f2d58b6eda01b19c49d8acf3cf" \
                 "caf447106ff04a5c38577397cba1e83e96610d0fe07c71cc9006f71cc26aae6917993a27d9eb2b22d2a907332d3c15" \
                 "c987aa50a50359091a65d784d082295a1e7ba86d2c"
Xtime2Sbox = bytes.fromhex(Xtime2Sbox_hex)

Xtime3Sbox_hex = "a584998d0dbdb1545003a97d1962e69a459d408715ebc90bec67fdeabff7965bc21cae6a5a41024f5cf43408937353" \
                 "3f0c52655e28a10fb509369b3d2669cd9f1b9e742e2db2eefbf64d61ce7b3e7197f568002c601fc8edbe46d94bded4" \
                 "e84a6b2ae516c5d75594cf100681f044bae3f3fec08aadbc4804dfc17563301a0e6d4c14352fe1a2cc3957f28247ac" \
                 "e72b95a098d17f667eab83ca29d33c79e21d763b564e1edb0a6ce45d6eefa6a8a4378b324359b78c64d2e0b4fa0725" \
                 "af8ee918d5886f7224f1c751237c9c21dddc86859042c4aad8050112a35ff9d0915827b93813b333bb7089a7b62292" \
                 "2049ff787a8ff88017da31c6b8c3b07711cbfcd63a"
Xtime3Sbox = bytes.fromhex(Xtime3Sbox_hex)

Rcon = bytes([0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36])

# ====================== 模拟原始自定义字符串字节函数 ======================
def strbyteget(buf:bytes, idx:int)->int:
    return buf[idx] & 0xFF

def strbyteset(buf:bytearray, idx:int, val:int):
    buf[idx] = val & 0xFF

def midstr(s:str, start:int, length:int)->str:
    return s[start:start+length]

def strright(s:str, n:int)->str:
    if n <=0:
        return ""
    return s[-n:]

def strupr(s:str)->str:
    return s.upper()

# ====================== 核心算法函数 VIN -> PIN ======================
def vin_to_pin(vin_str:str)->str:
    vin_str = vin_str.strip()
    if len(vin_str) !=17:
        raise Exception("VIN长度必须17位！")
    VIN_T = strupr(vin_str)

    Temp = midstr(VIN_T,0,8) + strright(VIN_T,8)
    CheckSum = 0
    PlainVin = bytearray(16)

    for i in range(16):
        c = Temp[i]
        if '0' <= c <= '9':
            val = ord(c) - 48
            CheckSum += val * strbyteget(PosOfVin,i)
        elif 'A' <= c <= 'Z':
            idx_ch = ord(c) - 65
            v = strbyteget(ChToNum, idx_ch)
            CheckSum += v * strbyteget(PosOfVin,i)
        strbyteset(PlainVin, i, ord(c))

    CheckSum = CheckSum % 11
    tp = str(CheckSum)
    vin_check_char = VIN_T[8]
    valid = False
    if tp == vin_check_char:
        valid = True
    elif tp == "10" and vin_check_char == 'X':
        valid = True
    if not valid:
        raise Exception(f"VIN校验位错误！VIN第9位[{vin_check_char}]，计算校验值={CheckSum}(10对应X)")

    # ============ 1. 初始化RoundKey(176字节) ============
    RoundKey = bytearray([0]*176)
    key_bytes = key_origin
    idx = 0
    while idx <16:
        if idx <8:
            strbyteset(RoundKey, idx, strbyteget(key_bytes, idx))
        else:
            strbyteset(RoundKey, idx, strbyteget(key_bytes, idx-8))
        idx +=1

    # AES密钥扩展 idx from4 to43
    idx =4
    while idx <44:
        w0 = strbyteget(RoundKey, idx*4 -4)
        w1 = strbyteget(RoundKey, idx*4 -3)
        w2 = strbyteget(RoundKey, idx*4 -2)
        w3 = strbyteget(RoundKey, idx*4 -1)
        tmp0,tmp1,tmp2,tmp3 = w0,w1,w2,w3
        if (idx %4)==0:
            tmp4 = tmp3
            tmp3 = strbyteget(Sbox, tmp0)
            tmp0 = strbyteget(Sbox, tmp1) ^ strbyteget(Rcon, idx//4)
            tmp1 = strbyteget(Sbox, tmp2)
            tmp2 = strbyteget(Sbox, tmp4)
        # w[i] = w[i-4] ^ tmp
        strbyteset(RoundKey, idx*4 +0, strbyteget(RoundKey, (idx-4)*4 +0) ^ tmp0)
        strbyteset(RoundKey, idx*4 +1, strbyteget(RoundKey, (idx-4)*4 +1) ^ tmp1)
        strbyteset(RoundKey, idx*4 +2, strbyteget(RoundKey, (idx-4)*4 +2) ^ tmp2)
        strbyteset(RoundKey, idx*4 +3, strbyteget(RoundKey, (idx-4)*4 +3) ^ tmp3)
        idx +=1

    # 源码额外混淆
    tmp3 = 0xA9
    strbyteset(RoundKey, 0, strbyteget(RoundKey,0) ^ tmp3)
    idx =1
    tmp0=0
    tmp1=1
    while idx <176:
        v = strbyteget(RoundKey, tmp0) ^ strbyteget(RoundKey, tmp1) ^ tmp3
        strbyteset(RoundKey, idx, v)
        tmp0 +=1
        tmp1 +=1
        tmp0 = tmp0 %176
        tmp0 = tmp0 %176
        tmp3 = (tmp3 +41) &0xFF
        idx +=1

    # ============ AES加密流程 ============
    state = bytearray(16)
    for i in range(16):
        strbyteset(state,i, strbyteget(PlainVin,i))

    # 初始轮密钥加 RoundKey[0~15]
    for i in range(16):
        strbyteset(state,i, state[i] ^ strbyteget(RoundKey,i))

    round =1
    while round <11:
        if round <10:
            # 完整轮：混合列(使用Xtime2/Xtime3)
            newstate = bytearray(16)
            s = state
            strbyteset(newstate,0, strbyteget(Xtime2Sbox,s[0]) ^ strbyteget(Xtime3Sbox,s[5]) ^ strbyteget(Sbox,s[10]) ^ strbyteget(Sbox,s[15]))
            strbyteset(newstate,1, strbyteget(Sbox,s[0]) ^ strbyteget(Xtime2Sbox,s[5]) ^ strbyteget(Xtime3Sbox,s[10]) ^ strbyteget(Sbox,s[15]))
            strbyteset(newstate,2, strbyteget(Sbox,s[0]) ^ strbyteget(Sbox,s[5]) ^ strbyteget(Xtime2Sbox,s[10]) ^ strbyteget(Xtime3Sbox,s[15]))
            strbyteset(newstate,3, strbyteget(Xtime3Sbox,s[0]) ^ strbyteget(Sbox,s[5]) ^ strbyteget(Sbox,s[10]) ^ strbyteget(Xtime2Sbox,s[15]))

            strbyteset(newstate,4, strbyteget(Xtime2Sbox,s[4]) ^ strbyteget(Xtime3Sbox,s[9]) ^ strbyteget(Sbox,s[14]) ^ strbyteget(Sbox,s[3]))
            strbyteset(newstate,5, strbyteget(Sbox,s[4]) ^ strbyteget(Xtime2Sbox,s[9]) ^ strbyteget(Xtime3Sbox,s[14]) ^ strbyteget(Sbox,s[3]))
            strbyteset(newstate,6, strbyteget(Sbox,s[4]) ^ strbyteget(Sbox,s[9]) ^ strbyteget(Xtime2Sbox,s[14]) ^ strbyteget(Xtime3Sbox,s[3]))
            strbyteset(newstate,7, strbyteget(Xtime3Sbox,s[4]) ^ strbyteget(Sbox,s[9]) ^ strbyteget(Sbox,s[14]) ^ strbyteget(Xtime2Sbox,s[3]))

            strbyteset(newstate,8, strbyteget(Xtime2Sbox,s[8]) ^ strbyteget(Xtime3Sbox,s[13]) ^ strbyteget(Sbox,s[2]) ^ strbyteget(Sbox,s[7]))
            strbyteset(newstate,9, strbyteget(Sbox,s[8]) ^ strbyteget(Xtime2Sbox,s[13]) ^ strbyteget(Xtime3Sbox,s[2]) ^ strbyteget(Sbox,s[7]))
            strbyteset(newstate,10, strbyteget(Sbox,s[8]) ^ strbyteget(Sbox,s[13]) ^ strbyteget(Xtime2Sbox,s[2]) ^ strbyteget(Xtime3Sbox,s[7]))
            strbyteset(newstate,11, strbyteget(Xtime3Sbox,s[8]) ^ strbyteget(Sbox,s[13]) ^ strbyteget(Sbox,s[2]) ^ strbyteget(Xtime2Sbox,s[7]))

            strbyteset(newstate,12, strbyteget(Xtime2Sbox,s[12]) ^ strbyteget(Xtime3Sbox,s[1]) ^ strbyteget(Sbox,s[6]) ^ strbyteget(Sbox,s[11]))
            strbyteset(newstate,13, strbyteget(Sbox,s[12]) ^ strbyteget(Xtime2Sbox,s[1]) ^ strbyteget(Xtime3Sbox,s[6]) ^ strbyteget(Sbox,s[11]))
            strbyteset(newstate,14, strbyteget(Sbox,s[12]) ^ strbyteget(Sbox,s[1]) ^ strbyteget(Xtime2Sbox,s[6]) ^ strbyteget(Xtime3Sbox,s[11]))
            strbyteset(newstate,15, strbyteget(Xtime3Sbox,s[12]) ^ strbyteget(Sbox,s[1]) ^ strbyteget(Sbox,s[6]) ^ strbyteget(Xtime2Sbox,s[11]))
            state = newstate
        else:
            # 最后一轮：S盒 + 行移位，无mixcolumn
            s = state.copy()
            strbyteset(state,0, strbyteget(Sbox, s[0]))
            strbyteset(state,4, strbyteget(Sbox, s[4]))
            strbyteset(state,8, strbyteget(Sbox, s[8]))
            strbyteset(state,12, strbyteget(Sbox, s[12]))

            tmp = strbyteget(Sbox, s[1])
            strbyteset(state,1, strbyteget(Sbox, s[5]))
            strbyteset(state,5, strbyteget(Sbox, s[9]))
            strbyteset(state,9, strbyteget(Sbox, s[13]))
            strbyteset(state,13, tmp)

            tmp = strbyteget(Sbox, s[2])
            strbyteset(state,2, strbyteget(Sbox, s[10]))
            strbyteset(state,10, tmp)

            tmp = strbyteget(Sbox, s[6])
            strbyteset(state,6, strbyteget(Sbox, s[14]))
            strbyteset(state,14, tmp)

            tmp = strbyteget(Sbox, s[15])
            strbyteset(state,15, strbyteget(Sbox, s[11]))
            strbyteset(state,11, strbyteget(Sbox, s[7]))
            strbyteset(state,7, strbyteget(Sbox, s[3]))
            strbyteset(state,3, tmp)

        # 轮密钥加，取RoundKey偏移 round*16
        key_off = round * 16
        for i in range(16):
            strbyteset(state,i, state[i] ^ strbyteget(RoundKey, key_off+i))
        round +=1

    # 生成PinStr 取前10字节 mod10 转字符串
    PinStr = ""
    for i in range(10):
        v = state[i] % 10
        PinStr += str(v)
    # 判断输出前8还是后8
    if midstr(PinStr,0,8) != "00000000":
        pinoutput = midstr(PinStr,0,8)
    else:
        pinoutput = strright(PinStr,8)
    return pinoutput


# ==================== 手机QPython 命令行交互入口 ====================
if __name__ == "__main__":
    print("===== 奇瑞VIN→PIN码计算工具(手机版) =====")
    while True:
        print("\n请输入17位VIN码，输入 q 退出程序")
        vin_input = input("VIN：").strip()
        if vin_input.lower() == "q":
            print("程序退出")
            break
        if not vin_input:
            continue
        try:
            pin_result = vin_to_pin(vin_input)
            print(f"✅ 计算PIN码：{pin_result}")
        except Exception as err:
            print(f"❌ 错误：{str(err)}")
