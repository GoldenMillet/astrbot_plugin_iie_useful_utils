from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import math

@register("iie_useful_utils", "Golden_millet", "提供一些实用的小功能。", "1.0", "https://github.com/GoldenMillet/astrbot_plugin_iie_useful_utils")
class MyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        # 开始限制的上下限
        self.up_bound = 70
        self.down_bound = 50

        # 初始化说话次数计数器存储路径
        self.data_dir = os.path.join("data", "UsefulUtils")
        os.makedirs(self.data_dir, exist_ok=True)
        self.user_counters_path = os.path.join(self.data_dir, "user_counters.json")

        # 计数器，记录每个用户说了多少话
        self.user_counters: Dict[str, int] = {}
        self.UU_load_counters()

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    # 注册指令的装饰器。指令名为 UU_help。注册成功后，发送 `/help` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("help")
    async def UU_help(self, event: AstrMessageEvent):
        """查看帮助""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)

        yield event.plain_result(f"微调工具箱：\n查看所有人的当前状态: /uuls\n清空某个人的数据: /uuclr\n修改上下限: /uuset") # 发送一条纯文本消息

    @filter.command("uuls")
    async def UU_ls(self, event: AstrMessageEvent):
        """查看所有人的记录"""
        yield event.plain_result(f"{str(self.user_counters)}")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uuclr")
    async def UU_clr(self, event: AstrMessageEvent, target: str):
        """删除某个人的信息"""
        try:
            del self.user_counters[target]
        except (json.JSONDecodeError, Exception) as e:
            temp = f"删除错误: {target} 不存在"
            logger.error(temp)
            yield event.plain_result(temp)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("uuset")
    async def UU_set(self, event: AstrMessageEvent, down: int, up: int):
        """设定上下限"""
        if (down < 0 or up < 0 or down >= up):
            temp = f"输入的数据非法！"
            logger.error(temp)
            yield event.plain_result(temp)
        else:
            self.down_bound = down
            self.up_bound = up
    
    def UU_load_counters():
        """加载用户说话次数记录"""
        # 加载计数器
        try:
            if os.path.exists(self.user_counters_path):
                with open(self.user_counters_path, 'r', encoding='utf-8') as f:
                    counters_temp = json.load(f)
                    # 确保所有值都是整数类型
                    for key in counters_temp:
                        self.user_counters[key] = int(self.counters_temp[key])
            else:
                self.user_counters = {}
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"加载用户发言计数器失败: {e}")
            self.user_counters = {}

    def UU_save_counters(self):
        """保存用户发言次数记录"""
        try:
            # 保存用户拦截计数器
            with open(self.user_counters_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_counters, f, ensure_ascii=False, indent=2)
            
            logger.debug("用户计数已保存")
        except Exception as e:
            logger.error(f"保存用户发言计数器失败: {e}")

    def UU_check_blacklist_status(self, event: AstrMessageEvent) -> Tuple[bool, Optional[str], Optional[str]]:
        """直接从配置检查消息是否来自指定用户"""
        sender_id = str(event.get_sender_id())

        # 直接从 self.config 获取最新的用户黑名单并检查
        listed_users = set(str(uid) for uid in self.config.get("signed_users", []))
        if sender_id in listed_users:
            return True, "user", sender_id

        return False, None, None
    
    @filter.event_message_type(filter.EventMessageType.ALL, priority=10)
    async def UU_check_list(self, event: AstrMessageEvent):
        """检查黑名单"""
        # 检查是否在已记录的列表中
        is_listed, blacklist_type, target_id = self.UU_check_blacklist_status(event)

        if not is_listed:
            # 如果不在列表里，则记录并设置为1
            sender_id = str(event.get_sender_id())            
            self.user_counters[sender_id] = 1
            return
        else:
            reply_probability = UU_calculate_reply_probability(self.user_counters[sender_id], self.down_bound, self.up_bound)
            reply_probability = max(0.0, min(1.0, reply_probability))

            # 决定是否回复
            should_suppress_reply = False
            random_value = random.random()
            sender_name = event.get_sender_name() or "未知用户"

            # 拦截
            if random_value > reply_probability:
                should_suppress_reply = True
                if log_messages:
                    message_preview = event.message_str[:50] + ("..." if len(event.message_str) > 50 else "")
                    log_identifier = f"用户: {sender_name}({target_id})"
                    logger.info(f"依照概率拦截 - {log_identifier},消息: {message_preview}, 拦截计数: {self.user_counters[sender_id]}, 当前概率为: {int(reply_probability * 100)}%")
            # 不拦截
            else:
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

    def UU_calculate_reply_probability(num: int, down: int, up: int):
        if num <= down:
            return float(1)
        elif num >= up:
            return float(0)
        else:
            ratio = (num - down) / (up - down)
            return 0.5 * (1 + math.cos(math.pi * ratio))
        
    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        self.UU_save_counters()
        logger.info("弱黑名单插件已停用，拦截计数已保存。")
