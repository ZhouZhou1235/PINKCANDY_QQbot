# 机器配置

class Config:
    bot_name = "PINKCANDY 粉糖QQ终端"
    bot_info = "\n===\n欢迎使用粉糖QQ终端，本机器正在开发中，随时可能停止工作或者报告错误！\n命令格式：粉糖终端 指令名 参数1,参数2......（如果有）\n===\n"
    qq_number = "3551851286"
    listen_qq_groups = [
        1050637546,
        751711878,
    ] # 监听的QQ群
    fixed_begin = "粉糖终端"
    function_commands = {
        "test": "测试",
        "hi": "问好",
        "help": "帮助",
        "random_get_member": "抽群友",
        "get_gallery_artwork": "来点粉糖",
    }
    function_command_info = [
        "测试：机器账号执行功能检查",
        "问好：Hello World",
        "帮助：打印这个帮助文本",
        "抽群友：随机抽个群友owo 可选参数为数字表示抽取数量",
        "来点粉糖：搜索粉糖画廊的作品 参数是标签 多个用空格隔开",
    ]