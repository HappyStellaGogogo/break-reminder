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
