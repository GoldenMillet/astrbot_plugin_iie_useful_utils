# 基本信息
C01_QQ_ID = $YOUR_BOT_QQ_ID_HERE$
C01_QQ_ID_STR = f"{C01_QQ_ID}"
C01_QQ_NICKNAME = $YOUR_BOT_NAME_HERE$
C01_GITHUB_URL = "https://github.com/GoldenMillet/astrbot_plugin_iie_useful_utils"

# /help帮助弹出的消息
C01_HELP_MSG_F = f"""iie抄底群机器人工具箱:

[📂常规]
查询机器人是否在线: /ping
保存一切数据: /uursa

[📂T01 - 发言动态限制]
水群统计: /uusq
查看所有人的当前交互次数: /uuls
清空某个人的数据: /uuclr <目标QQ号>
清空所有人的数据: /uuclrall
砍半所有人的数据: /uuhalf
修改上下限: /uuset <新下限> <新上限>

[📂T02 - 资料获取]
查看信工所导师信息(更新至2024年): /uuproflist
查看信工所往年考情分析(更新至2024年): /uudetails

[📂T03 - 随机老婆]
随机老婆: /uurw
清空配对数据: /uurwc
保存配对数据: /uurws
随机男娘: /uumtf

[📂T04 - ba塔罗牌]
ba塔罗牌: /uubac
"""

# /uuclrall弹出消息
C01_CLEAR_ALL_MSG = "已经重置本群内所有人的发言记数，现在大家又可以畅所欲言了！"

# 砍半弹出的消息
C01_HALF_ALL_MSG = "已经将所有人的发言条数记录除以二。"

# /ping弹出消息
C01_PING_MSG = "嗨呀，这里是信工所学妹啦～不是杭高院的智能菇学姐哦～我可不会回答你pong哟～"

# 输入了非法数据
C01_INVALID_DATA_MSG = "输入的数据非法！"

# 信工所导师名单与考情分析URL
C01_PROFFESOR_LIST_DIR = os.path.join("data", "plugins", "astrbot_plugin_iie_useful_utils", "locals", "2024_prof_list.pdf")
C01_EXAM_DETAILS_DIR = os.path.join("data", "plugins", "astrbot_plugin_iie_useful_utils", "locals", "2025_exam_report.pdf")

# 入群欢迎消息
C01_HELLO_MSG = """👋🎉欢迎加入中科院信工所考研群！

📂新进群的同学请先看群文件哟，有任何问题请咨询群内学长学姐哦～

🎓学妹强烈建议您看群文档里的录取信息资料，这里有最全的导师信息以及往年考情分析～

✨看到群里人多不要慌哟，其实他们都是已经上岸的学长学姐啦～

🍀😄在这里学妹预祝你考研顺利～
"""
C01_HELLO_IMG_DIR = os.path.join("data", "plugins", "astrbot_plugin_iie_useful_utils", "locals", "iie_bot_avatar.jpg")
C01_LEAVE_MSG = "太好了！又有群友退群了！这下竞争压力又小了一点哈哈哈哈哈哈哈哈哈哈～"

# 随机老婆文件保存地址
C01_RANDOM_WIFE_FILE_DIR = os.path.join("data", "UsefulUtils", "random_wife.txt")
C01_WIFES_ANIMATION_DIR = os.path.join("data", "plugins", "astrbot_plugin_iie_useful_utils", "locals", "wifes")

# BA塔罗牌文件地址
C01_BA_CARD_IMG_DIR = os.path.join("data", "plugins", "astrbot_plugin_iie_useful_utils", "locals", "ba_tarot_images")
C01_BA_CARD_INFO_DIR = os.path.join("data", "plugins", "astrbot_plugin_iie_useful_utils", "locals", "ba_tarot_images", "ba_card_info.txt")
