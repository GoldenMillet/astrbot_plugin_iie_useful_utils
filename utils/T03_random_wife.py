from astrbot.api import logger

from typing import Dict
import random

from ..constants.C01_help_msgs import *

# 抽老婆
def T03_random_wife(sender_id: str, usr_with_speak_beh: list, usr_wife: Dict[str, str]):
    is_hidden = False
    
    # 如果之前决定过是谁，那就直接反馈
    for key, value in usr_wife.items():
        if sender_id == key:
            return value, f"https://q4.qlogo.cn/headimg_dl?dst_uin={value}&spec=640", False

    # 先随机出来一个成员，为非法指n时为隐藏模式
    length = len(usr_with_speak_beh)
    random_index = random.randint(0, length + 2)
    if random_index < length and random_index >= 0:
        target_id = usr_with_speak_beh[random_index]
        avatar_url = f"https://q4.qlogo.cn/headimg_dl?dst_uin={target_id}&spec=640"
        is_hidden = False

        # 写入表格
        usr_wife[str(sender_id)] = target_id
    
    # 隐藏人物
    elif random_index == length:
        target_id = "御坂美琴"
        avatar_url = os.path.join(C01_WIFES_ANIMATION_DIR, "Misaka_Mikoto.jpg")
        is_hidden = True
    elif random_index == length + 1:
        target_id = "墨提斯Mortis"
        avatar_url = os.path.join(C01_WIFES_ANIMATION_DIR, "Mortis.jpg")
        is_hidden = True
    elif random_index == length + 2:
        target_id = "伊雷娜"
        avatar_url = os.path.join(C01_WIFES_ANIMATION_DIR, "Eleina.jpg")
        is_hidden = True
    else:
        """WIP - 其他人物待更新"""
        is_hidden = True

    return target_id, avatar_url, is_hidden

# 加载列表
def T03_save_speak_list(usr_with_speak_beh: list):
    with open(C01_RANDOM_WIFE_FILE_DIR, "w", encoding="utf-8") as f:
        for item in usr_with_speak_beh:
            f.write(item + "\n")

# 保存列表
def T03_load_speak_list(usr_with_speak_beh: list):
    try:
        with open(C01_RANDOM_WIFE_FILE_DIR, "r", encoding="utf-8") as f:
            usr_with_speak_beh = [line.strip() for line in f]
            return usr_with_speak_beh
    except Exception as e:
        logger.error(f"加载随机老婆发言记录失败: {e}")
        usr_with_speak_beh = []
    finally: 
        return []