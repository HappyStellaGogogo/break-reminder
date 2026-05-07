# 🍅 Break Reminder - 休息提醒小工具

每工作 45 分钟提醒你站起来休息 15 分钟，保护颈椎和眼睛！

基于 Python + Tkinter 实现，无需额外依赖，开箱即用。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 功能特性

- ⏱️ **自定义时长** — 工作和休息时间均可调节
- 🔔 **弹窗提醒** — 工作结束时置顶弹窗 + 系统提示音
- ⏸️ **暂停/继续** — 随时暂停计时，灵活掌控节奏
- 📊 **今日统计** — 记录已完成轮数和跳过休息次数
- 💬 **鼓励语** — 跳过休息时温馨提醒注意身体
- 🎨 **暗色主题** — 护眼深色 UI，长时间使用不刺眼
- 🖥️ **跨平台** — 支持 Windows / macOS / Linux
- 🚀 **开机自启动** — Windows 下可一键开启，目录改名后自动修复路径（Windows 专属）

## 🚀 快速开始

### 前置要求

- Python 3.10+（自带 Tkinter）

### 运行

```bash
python break_reminder.py
```

## 🎮 使用方式

1. 点击 **▶ 开始工作** 启动计时
2. 工作时间结束后弹窗提醒，可选择 **🧘 立即休息** 或 **💪 继续工作**
3. 休息结束后提醒开始下一轮工作
4. 随时可以 **⏸ 暂停** 或 **⏹ 重置**

## 🚀 Windows 开机自启动

### 启用方式

在应用界面中勾选 **🚀 开机自启动** 复选框即可。应用会将自启动命令写入注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`，使用 `pythonw.exe` 避免弹出控制台窗口。

### 目录改名/移动后的恢复

如果你重命名或移动了项目文件夹：

1. **当次重启**可能因旧路径失效而无法自启动——这是正常的
2. **从新目录手动启动一次**应用，程序会自动检测并修复注册表中的旧路径
3. 之后的开机自启动即恢复正常

### 手动排查

如果自启动仍然不工作，可以检查以下位置：

- **注册表**：`Win+R` → `regedit` → 导航到 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`，查看 `BreakReminder` 项的路径是否正确
- **Startup 文件夹**：`Win+R` → `shell:startup`，检查是否有指向旧路径的快捷方式
- **任务计划程序**：`Win+R` → `taskschd.msc`，搜索是否有相关计划任务

## 📸 截图

```
┌─────────────────────────────┐
│       💻 工作中              │
│         38:24                │
│  工作(分钟): 45  休息(分钟): 15 │
│  [▶ 开始] [⏸ 暂停] [⏹ 重置]  │
│  📊 已完成 2 轮 | 跳过 0 次   │
└─────────────────────────────┘
```

## 📄 License

MIT License
