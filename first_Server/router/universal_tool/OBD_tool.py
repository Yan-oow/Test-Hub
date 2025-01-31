import csv
import io
import re
from pydantic import BaseModel
from fastapi import APIRouter, Depends, UploadFile, File
from itertools import product, combinations
from fastapi.responses import JSONResponse
from collections import Counter

from sqlalchemy import column
from model.common import CommReturnObj
from router.universal_tool.OBD_model import ( 
    obdresult
)
router = APIRouter(prefix="/api")

@router.post("/upload_csv_file")
async def upload_csv_file(file: UploadFile = File(...)): 
    try:
        csv_content = await file.read()
        return JSONResponse(content={"message": "CSV file uploaded successfully"}, media_type="application/json")
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, media_type="application/json", status_code=500)

@router.post("/OBD_result")
async def OBD_result(csv_file: UploadFile = File(...)):  
    try:
        content = await csv_file.read()  
        data = extract_data_from_csv(content)
        sel = OBD_select(data)
        filtered_result, most_common = find_most_common_filtered(sel)
        count_result = figure_result(filtered_result)
        same = Filter_for_the_same(data,most_common)
        header = data[0]
        try:
            fw_name_index = header.index("FW_NAME")
        except ValueError:
            raise ValueError("FW_NAME 列未找到")

        filtered_rows = [header]  # 确保 header 是一个整体行
        filtered_rows.extend(row for row in data[1:] if row[fw_name_index] in most_common)


        return CommReturnObj(
            data=obdresult(
                data_required_choice = count_result,
                selected_data = same,
                Data = data
            )
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    

def Filter_for_the_same(data:list,result:list):
    output = []  # 存储结果
    visited = set()  # 用于记录已处理过的行，避免重复
    if data:
        output.append(data[0][1:7] + [data[0][0]])
    for res_row in result:
        matching_row = next((row for row in data if row[0] == res_row), None)
        if matching_row:
            target_columns = matching_row[1:7]
            similar_rows = [row for row in data if row[1:7] == target_columns]
            similar_keys = [row[0] for row in similar_rows]
            if tuple(target_columns) not in visited:
                visited.add(tuple(target_columns))
                output.append(target_columns + similar_keys)
    return output

def extract_data_from_csv(csv_content: bytes):
    """
    从 CSV 文件内容中提取特定列的数据，并返回二维数组。

    :param csv_content: CSV 文件的二进制内容 (bytes)
    :return: 提取的二维数组数据 (list)
    """
    decoded_content = csv_content.decode('utf-8')
    lines = decoded_content.splitlines()
    csv_reader = csv.reader(io.StringIO("\n".join(lines)), delimiter=';')

    header = next(csv_reader, None)
    second_row = next(csv_reader, None)

    target_columns = [
        "FW_NAME", 
        "FW_OPERATIONCYC", 
        "FW_CURABLE", 
        "FAILURE_CLASS", 
        "FW_RESTOREEVENTNEXTOC", 
        "DTC_OBD_CLASS",
        "SFB_TIME",
        "MON_DESC",
        "TEST_COMPLETE_MANEUVER_DESC"
    ]
    
    column_indices = [second_row.index(col) for col in target_columns if col in second_row]
    if len(column_indices) != len(target_columns):
        raise ValueError(f"CSV 缺少目标列，找到的列索引: {column_indices}")
    
    extracted_data = []
    extracted_data.append(target_columns)
    for row in csv_reader:
        if len(row) >= max(column_indices) + 1: 
            selected_row = [row[idx].strip('"') for idx in column_indices]  
            if selected_row[5] in ["ONE_TRIP", "TWO_TRIP"]:  
                extracted_data.append(selected_row)  

    return extracted_data




def OBD_select(data:list):
    # FW_OPERATIONCYC = set()
    # SFB_TIME = set()
    # for row in data_sel[1:]:
    #     FW_OPERATIONCYC.add(row[1])
    #     SFB_TIME.add(row[6])


    # SFB_TIME = [140,40,0]
    # FW_OPERATIONCYC = ["PowerCycle","OtherCycle","IgnitionCycle"]
    OBD_DTC_Class = ["ONE_TRIP","TWO_TRIP"]
    Curable_current_OC = ["YES","NO"]
    Restore_event_in_next_OC = ["YES","NO"]
    Failure_class = ["No good check","Clear failure state"]
    SFB_TIME = []
    FW_OPERATIONCYC = []

    for row in data[2:]:
    # 根据列的索引将值添加到相应的列表中
        if row[6] not in SFB_TIME:
            SFB_TIME.append(row[6])
        if row[1] not in FW_OPERATIONCYC:
            FW_OPERATIONCYC.append(row[1])
    print("SFB_TIME:", SFB_TIME)
    print("FW_OPERATIONCYC:", FW_OPERATIONCYC)
        
    
    columns_with_values = {
        "FW_OPERATIONCYC": FW_OPERATIONCYC,
        "FW_CURABLE": Curable_current_OC,
        "FAILURE_CLASS": Failure_class,
        "FW_RESTOREEVENTNEXTOC": Restore_event_in_next_OC,
        "DTC_OBD_CLASS": OBD_DTC_Class,
        "SFB_TIME": SFB_TIME,
    }

    # 生成列的两两组合
    column_combinations = list(combinations(columns_with_values.keys(), 2))

    result = []
    for col1, col2 in column_combinations:
        # 获取列的所有可能值
        values1 = columns_with_values[col1]
        values2 = columns_with_values[col2]

        # 对两列的值进行两两组合
        all_combinations = list(product(values1, values2))

        for combination in all_combinations:
            # 筛选符合组合条件的行
            filtered_rows = [
                row for row in data
                if row[data[0].index(col1)] == combination[0]
                and row[data[0].index(col2)] == combination[1]
            ]

            # 如果找到符合条件的行，则将组合键和值作为一条记录添加到结果列表
            value = [row[0] for row in filtered_rows]  # FW_NAME 对应的列是第 0 列
            result.append([(col1), combination[0], (col2), combination[1], value])

    return result


def find_most_common_filtered(result):
    """
    从 result 的第五列开始统计符合特定模式的元素出现次数，并返回出现次数最多的元素及其次数。
    
    :param result: 格式为 [(col1, value1, col2, value2, [list_of_FW_NAME]), ...] 的列表
    :return: 出现次数最多的符合条件的元素及其次数，例如 ('scl_123', 4)
    """
    # 用于统计的列表
    elements = []

    # 定义匹配的模式列表
    patterns = [
        r"^Scl.*$", 
        r"^scl.*$",  
        r"^ComScl.*$",  
        r"^RBNET.*$",  
        r".*InterruptionFailure$", 
        r".*LineGND$",  
        r"^RBHydraulicUndervoltage$",  
        r"^Wss_SignalLost_FL$",  
    ]

    # 合并所有模式为一个正则表达式
    combined_pattern = re.compile("|".join(patterns))
    most_common_elements = []

    while result:
        # 用于统计的列表
        elements = []

        # 提取第五列（即 FW_NAME 列）中的值并统计
        for row in result:
            if len(row) >= 5:
                for col in row[4:]:  # 从第五列到最后一列
                    elements.extend([
                        elem for elem in col  # 遍历每列的值
                        if combined_pattern.match(elem)  # 仅保留匹配的元素
                    ])
        
        # 使用 Counter 统计每个元素的出现次数
        counter = Counter(elements)

        # 找出出现次数最多的元素
        most_common = counter.most_common(1)
        if not most_common:
            break  # 如果没有符合条件的元素，跳出循环

        element, count = most_common[0]
        most_common_elements.append(element)
        print(element,count)
        # 从 result 中删除包含该元素的行
        result = [
            row for row in result
            if element not in row[4]
        ]

    result = [row for row in result if len(row) >= 5 and row[4]]

    return result,most_common_elements


def figure_result(result):
    # 用于统计的列表
    elements = []

    while result:
        # 提取第五列（即 FW_NAME 列）中的值并统计
        for row in result:
            if len(row) >= 5:
                for col in row[4:]:  
                    elements.extend([elem for elem in col])
        
        # 使用 Counter 统计每个元素的出现次数
        counter = Counter(elements)

        # 遍历 result，为每个元素添加出现次数
        for row in result:
            if len(row) >= 5:
                for i, col in enumerate(row[4:], start=4):
                    # 将元素和出现次数组合
                    row[i] = [[elem, f"{elem} {counter[elem]}"] for elem in col]

        return result

class DiffModel(BaseModel):
    result:obdresult = None