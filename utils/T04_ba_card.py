from ..constants.C01_help_msgs import *

def T04_loading_ba_card_info():
    file_path = C01_BA_CARD_INFO_DIR
    data_list = []

    # 扫描文件内容
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # 去掉空行

    # 三行一组
    for i in range(0, len(lines), 3):
        name = lines[i]
        up_text = lines[i + 1]
        down_text = lines[i + 2]
        group_index = i // 3
        img_url_up = os.path.join(C01_BA_CARD_IMG_DIR, f"tarot_{group_index}.png")
        img_url_down = os.path.join(C01_BA_CARD_IMG_DIR, f"tarot_{group_index}_down.png")
        data_list.append({
            "name": name,
            "up_text": up_text,
            "down_text": down_text,
            "img_url_up": img_url_up,
            "img_url_down": img_url_down
        })

    return data_list