from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent

import math
import json
import os
from typing import Dict, Tuple, Optional

# 通过上下限计算拦截概率
def T01_calculate_reply_probability(num: int, down_bound: int, up_bound: int):
    if num <= down_bound:
        return float(1)
    elif num >= up_bound:
        return float(0)
    else:
        ratio = (num - down_bound) / (up_bound - down_bound)
        return 0.5 * (1 + math.cos(math.pi * ratio))
    
def T01_load_counters(user_counters_path, user_counters: Dict[str, int]) -> Dict[str, int]:
    """加载用户说话次数记录"""
    # 加载计数器
    try:
        if os.path.exists(user_counters_path):
            with open(user_counters_path, 'r', encoding='utf-8') as f:
                counters_temp = json.load(f)
                # 确保所有值都是整数类型
                for key in counters_temp:
                    user_counters[key] = int(counters_temp[key])
        else:
            user_counters = {}
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"加载用户发言计数器失败: {e}")
        user_counters = {}
    finally:
        return user_counters
    
def T01_save_counters(user_counters_path, user_counters):
    """保存用户发言次数记录"""
    try:
        # 保存用户拦截计数器
        with open(user_counters_path, 'w', encoding='utf-8') as f:
            json.dump(user_counters, f, ensure_ascii=False, indent=2)
        
        logger.debug("用户计数已保存")
    except Exception as e:
        logger.error(f"保存用户发言计数器失败: {e}")


def T01_check_blacklist_status(user_counters, event: AstrMessageEvent) -> Tuple[bool, Optional[str], Optional[str]]:
    """直接从配置检查消息是否来自指定用户"""
    sender_id = str(event.get_sender_id())
    sender_name = str(event.get_sender_name())

    # 直接从 self.user_counters 获取最新的用户是否已经记录在列表内并检查
    if sender_id in user_counters:
        return True, sender_name, sender_id

    return False, None, None

