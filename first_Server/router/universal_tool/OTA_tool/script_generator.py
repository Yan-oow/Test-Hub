import os
from jinja2 import Environment, FileSystemLoader
import pathlib
import tempfile
import shutil
def gen_script_spec(config_list, fileA_path, template_path, logger, current_path, formatted_time):
    dir_path = tempfile.gettempdir()
    ota_dir = os.path.join(dir_path, "OTA")
    res_folder = pathlib.Path().joinpath(
        "res",
        "universal_tool",
        "OTA_tool",
        "template"
    )

    # 将模板路径传递给 Jinja2 环境
    env = Environment(loader=FileSystemLoader(str(res_folder)))

    # 加载模板
    tpl_script = env.get_template('OTA_Script.j2')
    tpl_spec = env.get_template('OTA_Spec.j2')
    tpl_testlist = env.get_template('OTA_testlist.j2')

    if not os.path.exists(f"{dir_path}\\OTA"):
        os.makedirs(f"{dir_path}\\OTA")

    with open(f'{dir_path}\\OTA\\RB_UNIVERSAL_01J.par', 'w', encoding='utf-8') as f:
        for item in config_list:
            try:
                render_content = tpl_script.render(
                    name=item["name"],
                    id=item["id"],
                    valid_value=item["valid_value"],
                    invalid_value=item["invalid_value"]
                )
                f.write(render_content)
            except Exception as e:
                logger.error(f'Nvm item: {item["name"]} Test Script Generate failed! Error: {e}')

    with open(f'{dir_path}\\OTA\\Testlist.txt', 'w', encoding='utf-8') as f:
        for item in config_list:
            try:
                render_content = tpl_testlist.render(
                    name=item["name"],
                    valid_value=item["valid_value"],
                    invalid_value=item["invalid_value"]
                )
                f.write(render_content)
            except Exception as e:
                logger.error(f'Nvm item: {item["name"]} Test list Generate failed! Error: {e}')

    with open(f'{dir_path}\\OTA\\OTA_Spec.csv', 'w', encoding='utf-8') as f:
        try:
            render_content = tpl_spec.render(config_list=config_list)
            f.write(render_content)
        except Exception as e:
            logger.error(f'OTA_Spec.csv generation failed! Error: {e}')
    
    # log_file_path = f'{current_path}\\logs\\log_{formatted_time}.txt'
    # if os.path.exists(log_file_path):
    #     # os.startfile(log_file_path)
    #     pass
    # else:
    #     logger.error(f"Log file {log_file_path} not found!")

    



    # 打包成 ZIP 文件
    zip_file_path = os.path.join(dir_path, f"OTA_{formatted_time}.zip")
    try:
        shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', ota_dir)
        print(f"ZIP file created: {zip_file_path}")
    except Exception as e:
        logger.error(f"Error creating ZIP file: {e}")
        return None

    # 返回 ZIP 文件路径
    print(f"ZIP file is ready for download at: {zip_file_path}")
    return zip_file_path







