import re

def error():
    print("An error occurred.")

# 字符串转十六进制数字, 默认都填的是十六进制数,所以直接return 数值
def turn_int(str1, digit):
    return int(str1)

# 根据Data_Size列的信息，获取当前item的最大和最小值
def find_range(range_num):
    hex_digits = range_num * 2  # 一字节对应两位
    min_value = "0" * hex_digits
    max_value = "F" * hex_digits
    return int(min_value, 16), int(max_value, 16)

# 扩展range的范围
def cnt_inv(ranges, digit):
    min_value, max_value = find_range(digit)
    max_range = ranges[0]
    for range in ranges[1:]:
        min_val, max_val = range
        if min_val < max_range[0]:
            max_range = (min_val, max_range[1])
        if max_val > max_range[1]:
            max_range = (max_range[0], max_val)
    if max_range[0] - 1 >= min_value:
        return max_range[0] - 1
    if max_range[1] + 1 <= max_value:
        return max_range[1] + 1
    return None

# 判断]和[之间是否有逗号
def has_comma_between(s):
    if s.count("[") == 1 and s.count("]") == 1 and s.count(",") == 1:
        return False
    elif s.count("[") == 1 and s.count("]") == 1 and s.count(",") > 1:
        return True
    start_index = [i for i, char in enumerate(s) if char == '['][1:]
    end_index = [i for i, char in enumerate(s) if char == ']'][:-1]
    for item in list(zip(end_index, start_index)):
        if abs(item[0] - item[1]) == 1:
            return False
        elif s[item[0]+1] == ",":
            return True

# 判断十进制字符串转换为十六进制之后有多少个byte
def calculate_bytes(str1):
    hex_value = hex(int(str1))[2:]
    if len(hex_value)%2==0:
        num_bytes = (len(hex_value)) // 2
    else:
        num_bytes = (len(hex_value) + 1) // 2
    return num_bytes

# 将十进制字符串转换为十六进制数,如果遇到负数进行补位的操作
def trans_decDtr_hex(str1):
    result = None
    if str1[0] == "-":
        complementary_code = "0x" + "F" * calculate_bytes(str1[1:])*2
        result = hex(int(str1) & int(complementary_code, 16))[2:]
    else:
        result = hex(int(str1))[2:]
    return result

# 处理十六进制数字符串，根据data_size进行补位和转大写，并且每隔两个字符加一个空格
def process_hex_string(hex_str, data_size=None):
    hex_str = hex_str.replace(' ', '')
    if data_size:
        while len(hex_str) < int(data_size)*2:
            hex_str = '0' + hex_str
    hex_str = hex_str.upper()
    hex_with_spaces = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2)) 
    return hex_with_spaces

# 1.1 模式 A - 十进制范围
def mode_A_dec(str1, digit):
    pattern = r'\[(-*\d+),\s*(-*\d+)\]'
    res_min = ""
    res_max = ""
    res_mid = ""
    matches = re.findall(pattern, str1)
    res = []
    for match in matches:
        left = trans_decDtr_hex(match[0])
        right = trans_decDtr_hex(match[1])
        #################################################################################################################################################################
        #mid = trans_decDtr_hex(str(int(int(match[0]) + int(match[1]) // 2)))#原版
        mid = trans_decDtr_hex(str(int(int(match[0]) + int(match[1])) // 2))
        ################################################################################################################################################################
        datasize = calculate_bytes(match[1])
        res_min = process_hex_string(left, datasize)
        res_max = process_hex_string(right, datasize)
        res_mid = process_hex_string(mid, datasize)
    res.append(res_min)
    res.append(res_mid)
    res.append(res_max)
    inv = ""
    res = sorted(res)
    if "empty" in res:
        hex_str = hex(int(res[0].replace(" ", ""), 16) - 1).upper()[2:]
        if len(hex_str) % 2 != 0:
            hex_str = "0" + hex_str
        inv = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
    else:
        inv = "empty"
    return res, inv

# 1.2 模式 A - 十六进制范围
def mode_A_hex(str1, data_size):
    if " " in str1:
        pattern = r'\[\s*([\dA-Fa-f]{2}(?:\s[\dA-Fa-f]{2})*)\s*,\s*([\dA-Fa-f]{2}(?:\s[\dA-Fa-f]{2})*)\s*\]'
        matches = re.findall(pattern, str1)
        res = []
        if matches:
            digit = len(matches[0][0].split(" "))
            for match in matches:
                left_dec = int(match[0].replace(" ", ""), 16)
                right_dec = int(match[1].replace(" ", ""), 16)
                min_dec = (left_dec + right_dec) // 2
                res.append(process_hex_string(trans_decDtr_hex(str(left_dec)), digit))
                res.append(process_hex_string(trans_decDtr_hex(str(min_dec)), digit))
                res.append(process_hex_string(trans_decDtr_hex(str(right_dec)), digit))
        else:
            print("No matches found in mode_A_hex")
        inv = ""
        res = sorted(res)
        if "empty" in res:
            hex_str = hex(int(res[0].replace(" ", ""), 16) - 1).upper()[2:]
            if len(hex_str) % 2 != 0:
                hex_str = "0" + hex_str
            inv = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
        else:
            inv = "empty"
        return res, inv

    elif "0x" in str1 or "0X" in str1:
        pattern = r'\[0[xX]([0-9a-fA-F]+),\s*0[xX]([0-9a-fA-F]+)\]'
        matches = re.findall(pattern, str1)
        res = []
        for match in matches:
            left_dec = int(match[0], 16)
            right_dec = int(match[1], 16)
            min_dec = (left_dec + right_dec) // 2
            res.append(process_hex_string(trans_decDtr_hex(str(left_dec)), data_size))
            res.append(process_hex_string(trans_decDtr_hex(str(min_dec)), data_size))
            res.append(process_hex_string(trans_decDtr_hex(str(right_dec)), data_size))
        inv = ""
        res = sorted(res)
        if "empty" in res:
            hex_str = hex(int(res[0].replace(" ", ""), 16) - 1).upper()[2:]
            if len(hex_str) % 2 != 0:
                hex_str = "0" + hex_str
            inv = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
        else:
            inv = "empty"
        return res, inv

    else:
        print("No valid pattern found in mode_A_hex")
        return [], "empty"

# 2. 模式 B
def mode_B(str1, datasize):    
    str1 = str1[1:-1]
    new_str_list = []
    if str1.find('{') != -1:
        pattern = re.compile(r'(?:{[^}]*}|[^,])+')
        matches = pattern.findall(str1)
        
        for match in matches:
            pattern = r'\{([^{}]*)\}'
            var_num_pair = re.findall(pattern, match)[0]
            if var_num_pair:
                var_num_list = var_num_pair.split(',')
                for v in var_num_list:
                    pattern = r'\{([^{}]*)\}'
                    result = re.sub(pattern, v, match)
                    new_str_list.append(result.strip())
    else:
        str_list = str1.split(',')
        new_str_list = []
        if "0x" in str(str_list[0]) or "0X" in str(str_list[0]):
            for s in str_list:
                new_str_list.append(process_hex_string(str(s[2:]),datasize))
        elif " " in str(str_list[0]):
            for s in str_list:
                new_str_list.append(s)
        else:
            for s in str_list:
                new_str_list.append(process_hex_string(trans_decDtr_hex(str(s)),datasize))
    inv = ""
    for ran in new_str_list:
        if ran.find("empty") == -1:
            inv = ran
            break
    return new_str_list, inv

# 3. 模式 C
def mode_C(str1, digit):
    str1 = str1[1:-1]
    str_list = re.split(r',(?=(?:[^\[\]]|\[[^\[\]]*\])*$)', str1)
    res = []
    for test_str in str_list:
        if test_str.find('[') != -1 and not has_comma_between(test_str):
            pattern = r'\[(-*[0-9a-fA-F]+),(-*[0-9a-fA-F]+)\]'
            res_min = ""
            res_max = ""
            res_mid = ""
            matches = re.findall(pattern, test_str)
            for match in matches:
                left = trans_decDtr_hex(match[0])
                right = trans_decDtr_hex(match[1])
                ##############################################################################################################################################################
                #mid = trans_decDtr_hex(str(int(int(match[0]) + int(match[1]) // 2)))#原版
                mid = trans_decDtr_hex(str(int(int(match[0]) + int(match[1]))// 2))
                ###################################################################################################################################################################
                datasize = calculate_bytes(match[1])
                res_min += process_hex_string(left,datasize)+" "
                res_max += process_hex_string(right,datasize)+" "
                res_mid += process_hex_string(mid,datasize)+" "
            res.append(res_min)
            res.append(res_mid)
            res.append(res_max)
        else:
            res.append(test_str)
    inv = ""
    res = sorted(res)
    if "empty" in res:
        hex_str = hex(int(res[0].replace(" ",""),16)-1).upper()[2:]
        inv = process_hex_string(hex_str,digit)
    else:
        inv = "empty"
    return res,inv

# 4. 模式 D
def mode_D(str1,datasize):
    result = []
    re_str = r'\[\s*([-0-9A-Fa-fx\s]+)[\s,]+([-0-9A-Fa-fx\s]+)\s*\]|((?!\s*e)\s*[-0-9A-Fa-fx\s]+)'
    matches = re.findall(re_str, str1)
    for match in matches:
        match_not_None = list(filter(None, match))
        if len(match_not_None) == 1:
            if "0x" in str(match_not_None[0]) or "0X" in str(match_not_None[0]):
                result.append(process_hex_string(str(match_not_None[0][2:]),datasize))
            elif " " in str(match_not_None[0]):
                result.append(match_not_None[0])
            else:
                result.append(process_hex_string(trans_decDtr_hex(str(match_not_None[0])),datasize))
        else:
            if " " in match[0] and " " in match[1]:
                left_dec = int(match[0].replace(" ",""),16)
                right_dec = int(match[1].replace(" ",""),16)
            elif "0x" in match[0] or "0X" in match[0]:
                left_dec = int(match[0],16)
                right_dec = int(match[1],16)
            else:
                left_dec = int(match[0])
                right_dec = int(match[1])
            min_dec = (left_dec+right_dec)//2
            result.append(process_hex_string(trans_decDtr_hex(str(left_dec)),datasize))
            result.append(process_hex_string(trans_decDtr_hex(str(min_dec)),datasize))
            result.append(process_hex_string(trans_decDtr_hex(str(right_dec)),datasize))
    if 'empty' in str1 or 'Empty' in str1:
        result.append('empty')
    return result

# 获取有效值 - True
def get_valid_value_true(str1, digit):
    if '{' not in str1 and '[' in str1 and not has_comma_between(str1):
        if "0x" in str1.split(",")[0] or "0x" in str1.split(",")[0] or " " in str1.split(",")[0]:
            res, inv = mode_A_hex(str1, digit)
        else:
            res, inv = mode_A_dec(str1, digit)
        return res, inv

    if '{' in str1 and '[' not in str1:
        new_str_list, inv = mode_B(str1, digit)
        return new_str_list, inv

    if '{' in str1 and '[' in str1 and not has_comma_between(str1):
        res, inv = mode_C(str1, digit)
        return res, inv

    if str1 == "":
        error()
    return [str1], None

# 获取有效值 - False
def get_valid_value_false(str1, digit):
    if '{' in str1 and '[' in str1 and not has_comma_between(str1):
        pattern = r'\{(-*[0-9a-fA-F]+),(-*[0-9a-fA-F]+)\}'
        res = set()
        matches = re.findall(pattern, str1)
        for match in matches:
            left = turn_int(match[0], digit)
            right = turn_int(match[1], digit)
            mid = int((left + right) / 2)
            res.add(str(left))
            res.add(str(right))
            res.add(str(mid))
        return list(res)  

    if '{' in str1 and '[' not in str1:
        res = []
        str1 = str1[1:-1]
        new_str_list = []
        if str1.find('{') != -1:
            pattern = re.compile(r'(?:{[^}]*}|[^,])+')
            matches = pattern.findall(str1)
            for match in matches:
                new_str_list.append(match.strip())
        else:
            new_str_list = str1.split(',')
            for index,item in enumerate(new_str_list):
                if item.startswith("0x") or item.startswith("0X"):
                    new_str_list[index] = process_hex_string(item[2:])
                elif "empty" in item or "Empty" in item:
                    new_str_list[index] = item
                else:
                    new_str_list[index] = process_hex_string(item)
        return new_str_list

    if '{' not in str1 and '[' in str1 and not has_comma_between(str1):
        if "0x" in str1.split(",")[0] or "0x" in str1.split(",")[0] or " " in str1.split(",")[0]:
            res,inv= mode_A_hex(str1, digit)
        else:
            res,inv= mode_A_dec(str1, digit)
        return res

    if '{' in str1 and '[' in str1 and has_comma_between(str1):
        res = mode_D(str1,digit)
        return res

    if str1 == "":
        error()
    return [str1]

# 获取无效值 - True
def get_invalid_value_true(str1, inv, datasize):
    patterns = [
        (r'^([0-9A-Fa-f]{2}\s*)+\s*\+\snot\s*(\{.*\})$', lambda m: m.group(0).split('+')[0]),  # 匹配 "00 00 00 00 + not {...}"
        (r'\{([^}]+)\}\s*not\s*\{(.+)\}', lambda m: m.group(1)),  # 匹配 "{i0,i1,i2,i3,...} not{...}"
        (r'\[(.*)\]\s*not\s*\{(.+)\}', lambda m: (m.group(1), m.group(2))),# 匹配 "[] not {}"
        (r'not\s*\[(.+)\]', lambda m: m.group(1)),# 匹配 "not []"
        (r'not\s*\{(.+)\}', lambda m: m.group(1))# 匹配 "not {}"
    ]
    cnt = 0
    for pattern, extractor in patterns:
        match = re.match(pattern, str1)
        if match:
            res = extractor(match)
            if cnt == 0:                 
                right_part = str(inv)
                if right_part.startswith(res):
                    return [right_part]
                else:
                    return [res + right_part]
            if cnt == 1:
                idx_list = res.split(',')
                ans = []
                for idx in idx_list:
                    idx = int(idx[1:])
                    num_list = inv.split(" ")
                    def find_not(num_str):
                        num = int(num_str, 16)
                        if num - 1 >= 0:
                            num -= 1
                            num_16 = hex(num)[2:].upper()
                            if len(num_16) % 2 != 0:
                                num_16 = '0' + num_16
                            formatted_hex = ' '.join(num_16[i:i+2] for i in range(0, len(num_16), 2))
                            return str(formatted_hex)
                        else:
                            num += 1
                            num_16 = hex(num)[2:].upper()
                            if len(num_16) % 2 != 0:
                                num_16 = '0' + num_16
                            formatted_hex = ' '.join(num_16[i:i+2] for i in range(0, len(num_16), 2))
                            return str(formatted_hex)
                    num_list[idx] = find_not(num_list[idx])
                    ans.append(' '.join(num_list))
                return ans
            if cnt == 2:
                range_list = res[0].split(',')
                not_value = res[1].split(',')
                res_range = []
                res_not = []
                for ran in range_list:
                    if "0x" in ran or "0X" in ran:
                        res_range.append(int(ran,16))
                    elif " " in ran:
                        res_range.append(int(ran.replace(" ",""),16))
                    else:
                        res_range.append(int(ran,16))
                for nv in not_value:
                    if "0x" in nv or "0X" in nv:
                        res_not.append(int(nv,16))
                    elif " " in nv:
                        res_not.append(int(nv.replace(" ",""),16))
                    else:
                        res_not.append(int(nv,16))
                full_range = set(range(res_range[0], res_range[1]+1))
                excluded_range = set(res_not)
                remaining_range = list(full_range - excluded_range)
                res_min = process_hex_string(trans_decDtr_hex(str(remaining_range[0])),datasize)
                res_mid = process_hex_string(trans_decDtr_hex(str(remaining_range[len(remaining_range)//2])),datasize)
                res_max = process_hex_string(trans_decDtr_hex(str(remaining_range[-1])),datasize)
                return [res_min,res_mid,res_max]
            if cnt == 3:
                result_3 = []
                max_value = (2 ** (int(datasize) * 8))-1
                left_value = res.split(',')[0]
                right_value = res.split(',')[1]
                if res.split(",")[0].upper().startswith("0X"):
                    full_range = [f"{i:0{int(datasize)*2}X}" for i in range(max_value+1)]
                    excluded_range = [f"{i:0{int(datasize)*2}X}" for i in range(int(left_value,16), int(right_value,16)+1)]
                    result_3 = [process_hex_string([value for value in full_range if value not in excluded_range][0],datasize),process_hex_string([value for value in full_range if value not in excluded_range][-1],datasize)]
                else:
                    full_range = [f"{i}" for i in range(max_value+1)]
                    excluded_range = [f"{i}" for i in range(int(left_value), int(right_value)+1)]
                    result_3 = [process_hex_string(trans_decDtr_hex([value for value in full_range if value not in excluded_range][0]),datasize),process_hex_string(trans_decDtr_hex([value for value in full_range if value not in excluded_range][-1]),datasize)]
                return result_3
            if cnt == 4:
                range_max= int('F'*2*int(datasize),16)
                not_value = res.split(',')
                res_range = [0,range_max]
                res_not = []
                for nv in not_value:
                    if "0x" in nv or "0X" in nv:
                        res_not.append(int(nv,16))
                    elif " " in nv:
                        res_not.append(int(nv.replace(" ",""),16))
                    else:
                        res_not.append(int(nv,16))
                full_range = set(range(res_range[0], res_range[1]+1))
                excluded_range = set(res_not)
                remaining_range = list(full_range - excluded_range)
                res_min = process_hex_string(trans_decDtr_hex(str(remaining_range[0])),datasize)
                res_mid = process_hex_string(trans_decDtr_hex(str(remaining_range[len(remaining_range)//2])),datasize)
                res_max = process_hex_string(trans_decDtr_hex(str(remaining_range[-1])),datasize)
                return [res_min,res_mid,res_max]
        cnt += 1
    return None

# 获取无效值 - False
def get_invalid_value_false(str1,datasize):
    patterns = [
        (r'^empty$', lambda m: m.group(0)),  # 匹配 "empty"
        (r'^!=\s*([0-9A-Fa-f]{2}\s*)$', lambda m: m.group(1)),  # 匹配 "!= 04"
        (r'^\{(.*)\}$', lambda m: m.group(1)),  # 匹配 "{01,02,03,04}，以及 {[00 03, FF FF], empty}"
        (r'(-*[0-9a-fA-F]+)', lambda m: m.group(1)) #匹配什么符号都不带的十进制数或者十六进制数
    ]
    cnt = 0
    for pattern, extractor in patterns:
        match = re.match(pattern, str1)
        if match:
            res = extractor(match)
            if cnt == 0:
                return [str(res)]
            if cnt == 1:
                def find_not(num_str):
                    num = int(num_str, 16)
                    if num - 1 >= 0:
                        num -= 1
                        num_16 = hex(num)[2:].upper()
                        if len(num_16) % 2 != 0:
                            num_16 = '0' + num_16
                        formatted_hex = ' '.join(num_16[i:i+2] for i in range(0, len(num_16), 2))
                        return str(formatted_hex)
                    else:
                        num += 1
                        num_16 = hex(num)[2:].upper()
                        if len(num_16) % 2 != 0:
                            num_16 = '0' + num_16
                        formatted_hex = ' '.join(num_16[i:i+2] for i in range(0, len(num_16), 2))
                        return str(formatted_hex)
                return [find_not(res)]
            if cnt == 2:
                if "[" not in res:
                    inv = res.split(',')
                    res_inv = []
                    for i in inv:
                        if i.startswith("0x") or i.startswith("0X"):
                            res_inv.append(process_hex_string(i[2:]))
                        else:
                            res_inv.append(process_hex_string(i))
                    return res_inv
                else:
                    result = mode_D(res,datasize)
                    return result
            if cnt==3:
                res_inv = ""
                if res.startswith("0x") or res.startswith("0X"):
                    res_inv = process_hex_string(res[2:])
                else:
                    res_inv = process_hex_string(res,datasize)
                return [res_inv]
        cnt += 1
    if '{' not in str1 and '[' in str1 and not has_comma_between(str1):
        if "0x" in str1.split(",")[0] or "0x" in str1.split(",")[0] or " " in str1.split(",")[0]:
            res,inv= mode_A_hex(str1, datasize)
        else:
            res,inv= mode_A_dec(str1, datasize)
        return res
    if "NOT same with selected running value" in str1:
        return ["00 "*datasize]
    return None
