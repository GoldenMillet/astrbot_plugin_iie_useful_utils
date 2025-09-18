from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
import random
import os
import json
from typing import Dict
from PIL import Image

from .constants.C01_help_msgs import * 
from .utils.T01_intercept_msgs import T01_calculate_reply_probability, T01_load_counters, T01_save_counters, T01_check_blacklist_status
from .utils.T03_random_wife import T03_random_wife, T03_load_speak_list, T03_save_speak_list, T03_repeater, T03_msg_statistics
from .utils.T04_ba_card import T04_loading_ba_card_info

@register("iie_useful_utils", "Golden_millet", "基于 AstrBot 的群机器人的功能拓展", "1.0", C01_GITHUB_URL)
class IIE_UU_Plugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # T01 - 发言开始限制的上下限
        self.up_bound = 40
        self.down_bound = 20

        # T01 - 初始化说话次数计数器存储路径
        self.data_dir = os.path.join("data", "UsefulUtils")
        os.makedirs(self.data_dir, exist_ok=True)
        self.user_counters_path = os.path.join(self.data_dir, "user_counters.json")

        # T01 - 计数器，记录每个用户说了多少话
        self.user_counters: Dict[str, int] = {}
        self.user_counters = T01_load_counters(self.user_counters_path, self.user_counters)
        logger.info(f"发言名单已加载，用户名单共 {len(self.user_counters)} 个")

        # T03 - 抽随机老婆
        self.usr_with_speak_beh: list = T03_load_speak_list([])
        self.usr_wife: Dict[str, str] = {}

        # T03 - 水群统计（qq号，qq昵称，发言次数）
        self.msg_statistics: tuple[str, str, int] = None
        self.msg_statistics_list = []

        # T03 - 复读机
        self.history_meg_list = ["", "", ""]
        self.msg_repeat = ""

        # T04 - ba塔罗牌
        self.ba_card_info = T04_loading_ba_card_info()

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    @filter.command("help")
    async def UU_help(self, event: AstrMessageEvent):
        """查看帮助""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)

        yield event.plain_result(C01_HELP_MSG_F) # 发送一条纯文本消息

    @filter.command("ping")
    async def UU_pingpong(self, event: AstrMessageEvent):
        """ping pong"""
        yield event.plain_result(C01_PING_MSG)
    
    #####################
    ######## T01 ########
    ##################### 

    @filter.command("uuls", alias={"冷暴力列表", "冷暴力名单"})
    async def UU_ls(self, event: AstrMessageEvent):
        """查看所有人的记录"""
        ret = "🧊🧊🧊 冷暴力名单 🧊🧊🧊\n"

        # 要按照顺序输出
        counters_temp: dict = self.user_counters
        for key, value in sorted(counters_temp.items(), key=lambda item: item[1], reverse=True):
            deny_probability_temp = 100 - int(T01_calculate_reply_probability(value, self.down_bound, self.up_bound) * 100)
            if value >= 1:
                ret = ret + f"用户 - {key}\n累计对话次数: {value} 次\n下次对话拒绝概率为: {deny_probability_temp}%\n\n"

        # 折叠为合并转发
        node = Comp.Node(
            uin=C01_QQ_ID,
            name=C01_QQ_NICKNAME,
            content=[
                Comp.Plain(ret[:-2])
            ]
        )
        yield event.chain_result([node])

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uuclr")
    async def UU_clr(self, event: AstrMessageEvent, target: str):
        """删除某个人的信息"""
        try:
            del self.user_counters[target]
            temp = f"已经重置 {target} 的发言记录"
            logger.error(temp)
            yield event.plain_result(temp)
        except (json.JSONDecodeError, Exception) as e:
            temp = f"删除错误: {target} 不存在"
            logger.error(temp)
            yield event.plain_result(temp)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uuclrall")
    async def UU_clr_all(self, event: AstrMessageEvent):
        """删除全部人的发言记录"""
        self.user_counters = {}
        temp = C01_CLEAR_ALL_MSG
        logger.error(temp)
        yield event.plain_result(temp)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uuhalf")
    async def UU_half(self, event: AstrMessageEvent):
        """砍半全部人的发言记录"""
        for key, value in self.user_counters.items():
            self.user_counters[key] = int(value / 2)

        temp = C01_HALF_ALL_MSG
        logger.error(temp)
        yield event.plain_result(temp)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uuset")
    async def UU_set(self, event: AstrMessageEvent, down: int, up: int):
        """设定上下限"""
        if (down < 0 or up < 0 or down >= up):
            temp = C01_INVALID_DATA_MSG
            logger.error(temp)
            yield event.plain_result(temp)
        else:
            self.down_bound = down
            self.up_bound = up

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uusave")
    async def UU_save(self, event: AstrMessageEvent):
        """保存当前计数至本地"""
        T01_save_counters(self.user_counters_path, self.user_counters)
        yield event.plain_result("计数器保存成功")

    @filter.event_message_type(filter.EventMessageType.ALL, priority=10)
    async def UU_check_list(self, event: AstrMessageEvent):
        """收到发言要触发的内容"""

        # T03 - 抽老婆，水群统计用
        if event.get_sender_id() not in self.usr_with_speak_beh:
            self.usr_with_speak_beh.append(event.get_sender_id())
        self.msg_statistics_list = T03_msg_statistics(self.msg_statistics_list, event.get_sender_id(), event.get_sender_name())

        # T03 - 复读机用
        if event.get_message_str() != None:
            if self.msg_repeat != event.get_message_str():
                self.history_meg_list, self.msg_repeat, need_repeat = T03_repeater(self.history_meg_list, event.get_message_str())
                if need_repeat:
                    yield event.plain_result(event.get_message_str())

        # 以下内容是只有在被at时才会触发的
        if event.is_at_or_wake_command == False:
            return

        # 检查是否在已记录的列表中
        is_listed, target_name, target_id = T01_check_blacklist_status(self.user_counters, event)
        sender_id = str(event.get_sender_id())

        if not is_listed:
            # 如果不在列表里，则记录并设置为1
            self.user_counters[sender_id] = 1
            # logger.info(f"debug==============1")
            return
        else:
            values_temp = self.user_counters[sender_id]
            # logger.info(f"debug=============={values_temp}")
            reply_probability = T01_calculate_reply_probability(values_temp, self.down_bound, self.up_bound)
            reply_probability = max(0.0, min(1.0, reply_probability))

            # 决定是否回复
            should_suppress_reply = False
            random_value = random.random()
            sender_name = target_name or "未知用户"

            # 拦截的情况
            if random_value > reply_probability:
                should_suppress_reply = True
                message_preview = event.message_str[:50] + ("..." if len(event.message_str) > 50 else "")
                log_identifier = f"用户: {sender_name}({target_id})"
                logger.info(f"依照概率拦截 - {log_identifier},消息: {message_preview}, 拦截计数: {self.user_counters[sender_id]}, 当前概率为: {int(reply_probability * 100)}%")
            
            # 不拦截，如果是管理员或者没有at，则跳过
            else:
                if not event.is_admin():
                    self.user_counters[sender_id] += 1                

        # 设置事件标记
        event.set_extra("useful_utils_suppress_reply", should_suppress_reply)

    @filter.on_decorating_result(priority=1)
    async def UU_suppress_reply_if_marked(self, event: AstrMessageEvent):
        """清空最终要发送的消息链"""
        if event.get_extra("useful_utils_suppress_reply") is True:
            log_messages = bool(self.config.get("log_blocked_messages", True))
            current_result = event.get_result()
            if current_result and hasattr(current_result, 'chain'):
                if log_messages:
                    sender_id = str(event.get_sender_id())
                    group_id = event.get_group_id()
                    identifier = f"群聊 {group_id} 中的用户 {sender_id}" if group_id else f"用户 {sender_id}"
                    original_chain_length = len(current_result.chain)
                    logger.info(f"依照概率禁言：替换 {identifier} 的待发送消息链，长度: {original_chain_length}")
                
                # 不完全清空消息链，而是替换为一个空文本消息
                # 这样可以避免其他插件尝试访问chain[0]时出现索引越界错误
                from astrbot.api.message_components import Plain
                current_result.chain.clear()
                current_result.chain.append(Plain(text=""))
            
            # 清除标记，避免对同一事件对象的后续影响
            event.set_extra("useful_utils_suppress_reply", False)

    @filter.command("uusq", alias={"水群统计", "今日水群", "水群排行", "水群排名"})
    async def UU_msg_statistics(self, event: AstrMessageEvent):
        """水群统计输出"""
        ret = "🏆群聊活跃度排行榜\n\n"
        rank = 1
        for item in sorted(self.msg_statistics_list, key=lambda x: x[2], reverse=True):
            if rank == 1:
                ret = ret + "🥇"
            elif rank ==  2:
                ret = ret + "🥈"
            elif rank ==  3:
                ret = ret + "🥉"
            elif rank > 10:
                break
            else:
                ret = ret + "🎖️"
            ret = ret + f"用户 - {item[1]}\n累计水群次数: {item[2]} 条\n\n"
            rank += 1
        yield event.plain_result(ret)
       
    #####################
    ######## T02 ########
    ##################### 

    @filter.command("uuproflist", alias={"导师列表", "导师名单"})
    async def UU_professor_list(self, event: AstrMessageEvent):
        """查看信工所当前导师名单"""
        chain = [
            Comp.At(qq=event.get_sender_id()), # At 消息发送者
            Comp.Plain("这是去年整理的信工所各研究室导师名单哦："),
        ]
        yield event.chain_result(chain)

        file = Comp.File(name="信工所导师名单.pdf", file=C01_PROFFESOR_LIST_DIR, url="")
        yield event.chain_result([file])

    @filter.command("uudetails", alias={"考试资料", "考情分析"})
    async def UU_exam_details(self, event: AstrMessageEvent):
        """查看信工所往年资料"""
        chain = [
            Comp.At(qq=event.get_sender_id()), # At 消息发送者
            Comp.Plain("这是根据上一届入学同学整理的考情分析哦："),
        ]
        yield event.chain_result(chain)

        file = Comp.File(name="信工所考情分析.pdf", file=C01_EXAM_DETAILS_DIR, url="")
        yield event.chain_result([file])

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def UU_handle_group_add_leave(self, event: AstrMessageEvent):
        """群增加人员发消息"""

        # 确保一定是群成员增加才触发
        if not hasattr(event, "message_obj") or not hasattr(event.message_obj, "raw_message"):
            return
        raw_message = event.message_obj.raw_message
        if not raw_message or not isinstance(raw_message, dict):
            return
        if raw_message.get("post_type") != "notice":
            return
        if raw_message.get("notice_type") == "group_increase":
            # 群成员增加事件
            chain = [
                Comp.Plain(C01_HELLO_MSG),
                Comp.Image.fromFileSystem(C01_HELLO_IMG_DIR)
            ]
            yield event.chain_result(chain)
        elif raw_message.get("notice_type") == "group_decrease":
            # 群成员减少事件
            yield event.plain_result(C01_LEAVE_MSG)
        else:
            return
    
    #####################
    ######## T03 ########
    ##################### 

    @filter.command("uurw", alias={"随机老婆", "今日老婆"})
    async def UU_random_wife(self, event: AstrMessageEvent):
        """抽老婆"""
        sender_id_str = event.get_sender_id()
        target_id_str, avatar_url, is_hidden = T03_random_wife(sender_id_str, self.usr_with_speak_beh, self.usr_wife)

        # 发送文本 - 隐藏
        if is_hidden:
            chain = [
                Comp.At(qq=sender_id_str),
                Comp.Plain(" 你的今日老婆是: "),
                Comp.Image.fromFileSystem(avatar_url),
                Comp.Plain(target_id_str)
            ]
            yield event.chain_result(chain)

        # 发送文本 - 非隐藏
        else:
            chain = [
                Comp.At(qq=sender_id_str),
                Comp.Plain(" 你的今日老婆是: "),
                Comp.Image.fromURL(avatar_url),
                Comp.At(qq=target_id_str)
            ]
            yield event.chain_result(chain)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uurwc", alias={"清空老婆"})
    async def UU_random_wife_clear(self, event: AstrMessageEvent):
        """清空老婆数据"""
        self.usr_wife = {}
        yield event.plain_result("抽老婆配对数据已清空！")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uurws")
    async def UU_random_wife_save(self, event: AstrMessageEvent):
        """保存随机老婆发言数据"""
        T03_save_speak_list(self.usr_with_speak_beh)
        yield event.plain_result("抽老婆发言数据已保存！")

    @filter.command("uumtf", alias={"随机男娘", "今日男娘"})
    async def UU_random_mtf(self, event: AstrMessageEvent):
        """抽男娘"""
        random_index = random.randint(0, len(self.msg_statistics_list) - 1)
        random_item = self.msg_statistics_list[random_index]

        # 折叠为合并转发
        node = Comp.Node(
            uin = random_item[0],
            name = random_item[1],
            content = [
                Comp.Plain("我是男娘")
            ]
        )
        yield event.chain_result([node])

    #####################
    ######## T04 ########
    ##################### 

    @filter.command("uubac", alias={"ba塔罗牌", "塔罗牌"})
    async def UU_random_ba_card(self, event: AstrMessageEvent):
        """ba塔罗牌功能"""
        length = len(self.ba_card_info)
        random_card_index = random.randint(0, length - 1)
        random_card_updown = random.randint(0, 1)
        if random_card_updown == 0:
            updown_desc = "顺位"
            updown_short = "up"
        else:
            updown_desc = "逆位"
            updown_short = "down"

        desc_temp = f"""
老师，这是您抽的塔罗牌:

{self.ba_card_info[random_card_index]["name"]}({updown_desc})

{self.ba_card_info[random_card_index][updown_short + "_text"]}
        """

        chain = [
            Comp.At(qq=event.get_sender_id()),
            Comp.Plain(desc_temp),
            Comp.Image.fromFileSystem(self.ba_card_info[random_card_index]["img_url_" + updown_short])
        ]
        yield event.chain_result(chain)

    #####################
    ######## etc ########
    ##################### 

    @filter.command("uursa", alias={"全部保存", "保存全部"})
    async def UU_save_all(self, event: AstrMessageEvent):
        """保存插件内所有数据"""
        T01_save_counters(self.user_counters_path, self.user_counters)
        T03_save_speak_list(self.usr_with_speak_beh)
        yield event.plain_result("插件内所有数据已经保存")
 
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        T01_save_counters(self.user_counters_path, self.user_counters)
        T03_save_speak_list(self.usr_with_speak_beh)
        logger.info("iie调整插件已停用，各种数据已保存。")
