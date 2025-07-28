from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp
import random
import os
import json
from typing import Tuple, Optional, Dict

from .constants.C01_help_msgs import C01_HELP_MSG_F, C01_CLEAR_ALL_MSG, C01_PING_MSG, C01_INVALID_DATA_MSG, C01_QQ_ID, C01_QQ_NICKNAME, C01_PROFFESOR_LIST_URL, C01_EXAM_DETAILS_URL
from .utils.T01_intercept_msgs import T01_calculate_reply_probability, T01_load_counters, T01_save_counters, T01_check_blacklist_status

@register("iie_useful_utils", "Golden_millet", "基于 AstrBot 的群机器人的功能拓展", "1.0", "https://github.com/GoldenMillet/astrbot_plugin_iie_useful_utils")
class IIE_UU_Plugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # T01 - 发言开始限制的上下限
        self.up_bound = 50
        self.down_bound = 25

        # T01 - 初始化说话次数计数器存储路径
        self.data_dir = os.path.join("data", "UsefulUtils")
        os.makedirs(self.data_dir, exist_ok=True)
        self.user_counters_path = os.path.join(self.data_dir, "user_counters.json")

        # T01 - 计数器，记录每个用户说了多少话
        self.user_counters: Dict[str, int] = {}
        self.user_counters = T01_load_counters(self.user_counters_path, self.user_counters)
        logger.info(f"发言名单已加载，用户名单共 {len(self.user_counters)} 个")

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    # 注册指令的装饰器。指令名为 UU_help。注册成功后，发送 `/help` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("help")
    async def UU_help(self, event: AstrMessageEvent):
        """查看帮助""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)

        yield event.plain_result(C01_HELP_MSG_F) # 发送一条纯文本消息

    @filter.command("uuls")
    async def UU_ls(self, event: AstrMessageEvent):
        """查看所有人的记录"""
        ret = ""
        for key, value in self.user_counters.items():
            deny_probability_temp = 100 - int(T01_calculate_reply_probability(value, self.down_bound, self.up_bound) * 100)
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
        """删除全部人的信息"""
        self.user_counters = {}
        temp = C01_CLEAR_ALL_MSG
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

    @filter.command("ping")
    async def UU_pingpong(self, event: AstrMessageEvent):
        """ping pong"""
        yield event.plain_result(C01_PING_MSG) # 发送一条纯文本消息
    
    @filter.command("uuproflist")
    async def UU_professor_list(self, event: AstrMessageEvent):
        """查看信工所当前导师名单"""
        chain = [
            Comp.At(qq=event.get_sender_id()), # At 消息发送者
            Comp.Plain("这是去年整理的信工所各研究室导师名单哦："),
        ]
        yield event.chain_result(chain)

        file = Comp.File(name="信工所导师名单.pdf", file="", url=C01_PROFFESOR_LIST_URL)
        yield event.chain_result([file])

    @filter.command("uudetails")
    async def UU_exam_details(self, event: AstrMessageEvent):
        """查看信工所往年资料"""
        chain = [
            Comp.At(qq=event.get_sender_id()), # At 消息发送者
            Comp.Plain("这是根据上一届入学同学整理的考情分析哦："),
        ]
        yield event.chain_result(chain)

        file = Comp.File(name="信工所考情分析.pdf", file="", url=C01_EXAM_DETAILS_URL)
        yield event.chain_result([file])
    
    @filter.event_message_type(filter.EventMessageType.ALL, priority=10)
    async def UU_check_list(self, event: AstrMessageEvent):
        """检查名单"""

        # 如果是管理员或者没有at，则跳过
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
        
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        T01_save_counters(self.user_counters_path, self.user_counters)
        logger.info("iie调整插件已停用，拦截计数已保存。")
