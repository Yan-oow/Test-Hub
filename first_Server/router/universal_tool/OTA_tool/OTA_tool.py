
from io import BytesIO
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from flask import jsonify, send_file
import pandas as pd
import os
import sys

from pydantic import FilePath

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from typing import List
from my_logger_setup import setup_logger
import script_generator
from model.common import CommReturnObj
router = APIRouter(prefix="/api")

import my_data_processing as dp

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VERSION = 'V1.2'
logger, log_filename, formatted_time, current_path = setup_logger(VERSION)



router = APIRouter(prefix="/api")

@router.post("/upload_excel_File")
async def upload_excel_File(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsm'):
        raise HTTPException(status_code=400, detail="File format not supported. Please upload an xlsm file.")

    
    return {"message": "File uploaded successfully"}



@router.post("/OTA_result")
async def OTA_result(file: UploadFile = File(...)):
    try:
        # Step 1: 保存上传的文件到临时路径
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # 保存模板路径
        base_path = os.path.abspath(".")
        template_path = os.path.join(base_path, 'template')

        # Step 2: 使用 Pandas 读取 Excel 文件
        df = pd.read_excel(temp_file_path, header=1)

        # Step 3: 数据过滤
        filter_df = df[~(df.iloc[:, 2].str.strip().str.lower() == 'bootloader')]
        filter_df = filter_df[
            ~filter_df.iloc[:, 10]
            .str.strip()
            .str.lower()
            .str.contains('no incompatible value|other value are not ok|not used in sw|na', na=False)
            & filter_df.iloc[:, 10].notna()
        ]

        # Step 4: 数据处理和配置生成
        config_list = []
        for index, row in filter_df.iterrows():
            config_dict = {}
            config_dict["name"] = row.iloc[1]
            config_dict["id"] = dp.process_hex_string(hex(int(row.iloc[0]))[2:], 2)
            in_content = str(row.iloc[10]).replace('，', ",")
            datasize = int(row["Data_Size"])
            content = row.iloc[8]
            content = str(content).replace('，', ",")
            if 'not' in in_content:
                try:
                    valid_value, inv = dp.get_valid_value_true(content.strip(), datasize)
                    if valid_value is None:
                        raise Exception("maybe missing {} or []")
                    else:
                        config_dict["valid_value"] = valid_value
                except Exception as e:
                    print(f"Format is not correct! ======> NVM item: {config_dict['name']}, Running Range - Value: {content} <======. The error is {e}")

                try:
                    invalid_value = dp.get_invalid_value_true(in_content.strip(), inv, datasize)
                    if invalid_value is None:
                        raise Exception("maybe missing {} or []")
                    else:
                        config_dict["invalid_value"] = invalid_value
                except Exception as e:
                    print(f"Format is not correct! ======> NVM item: {config_dict['name']}, Incompatible Values: {in_content} <======. The error is {e}")
            elif (content.find("NA") != -1 or content.find("na") != -1 or content.find("same with current value before OTA") != -1) and in_content.find("not") != -1:
                config_dict["valid_value"] = []
                try:
                    invalid_value = dp.get_invalid_value_true(in_content.strip(), inv, datasize)
                    if invalid_value is None:
                        raise Exception("maybe missing {} or []")
                    else:
                        config_dict["invalid_value"] = invalid_value
                except Exception as e:
                    print(f"Format is not correct! ======> NVM item: {config_dict['name']}, Incompatible Values: {in_content} <======. The error is {e}")
            elif (content.find("NA") != -1 or content.find("na") != -1 or content.find("same with current value before OTA") != -1) and in_content.find("not") == -1:
                config_dict["valid_value"] = []
                try:
                    invalid_value = dp.get_invalid_value_false(in_content.strip(), datasize)
                    if invalid_value is None:
                        raise Exception("maybe missing {} or []")
                    else:
                        config_dict["invalid_value"] = invalid_value
                except Exception as e:
                    print(f"Format is not correct! ======> NVM item: {config_dict['name']}, Incompatible Values: {in_content} <======. The error is {e}")
            else:
                try:
                    valid_value = dp.get_valid_value_false(content.strip(), datasize)
                    if valid_value is None:
                        raise Exception("maybe missing {} or []")
                    else:
                        config_dict["valid_value"] = valid_value
                except Exception as e:
                    print(f"Format is not correct! ======> NVM item: {config_dict['name']}, Running Range - Value: {content} <======. The error is {e}")

                try:
                    invalid_value = dp.get_invalid_value_false(in_content.strip(), datasize)
                    if invalid_value is None:
                        raise Exception("maybe missing {} or []")
                    else:
                        config_dict["invalid_value"] = invalid_value
                except Exception as e:
                    print(f"Format is not correct! ======> NVM item: {config_dict['name']}, Incompatible Values: {in_content} <======. The error is {e}")
            config_list.append(config_dict)

        zip_file_path = script_generator.gen_script_spec(config_list, temp_file_path, template_path, logger, current_path, formatted_time)
        # return {"file_path": zip_file_path}
        # Step 5: 封装数据为 OtaResult 格式
        # return JSONResponse(
        #     content={
        #         "code": 200,
        #         "message": "Success",
        #         "data": {
        #             "Data": zip_file_path
        #         }
        #     },
        #     status_code=200
        # )
        file_size = os.path.getsize(zip_file_path)
        print(f"File size: {file_size} bytes")
        if os.path.exists(zip_file_path):
            return FileResponse(path=zip_file_path,media_type="application/zip",filename="processed_file.zip")

    except Exception as e:
        return JSONResponse(
            content={
                "code": 500,
                "message": f"Error during file processing: {str(e)}"
            },
            status_code=500
        )
    
