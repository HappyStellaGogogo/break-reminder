#!/usr/bin/env python3
"""
休息提醒小工具 — Break Reminder
每工作 45 分钟提醒站起来休息 15 分钟。
Python + Tkinter 实现，无需额外依赖。
"""

import tkinter as tk
from tkinter import font as tkfont
import platform
import sys

# ---------------------------------------------------------------------------
# 跨平台提示音
# ---------------------------------------------------------------------------

def play_alert_sound():
    """播放系统提示音（跨平台）。"""
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
        else:
            # Linux / 其他: 终端响铃
            print("\a", end="", flush=True)
    except Exception:
        print("\a", end="", flush=True)


# ---------------------------------------------------------------------------
# 状态常量
# ---------------------------------------------------------------------------
STATE_IDLE = "IDLE"
STATE_WORKING = "WORKING"
STATE_BREAK_PROMPT = "BREAK_PROMPT"
STATE_RESTING = "RESTING"
STATE_PAUSED = "PAUSED"

# ---------------------------------------------------------------------------
# 跳过休息鼓励语
# ---------------------------------------------------------------------------
SKIP_MESSAGES = [
    "这是你今天第 {n} 次跳过休息哦～偶尔可以，但别忘了身体最重要！💪",
    "第 {n} 次跳过了！下次一定要休息哦，你的身体在默默记账呢 📝",
]
SKIP_MESSAGE_URGENT = "已经跳过 {n} 次了！求求你休息一下吧，你的颈椎在向你呼救 🆘"

# ---------------------------------------------------------------------------
# 跳过休息后，下次提醒时的肉麻关怀语
# ---------------------------------------------------------------------------
CARING_MESSAGES = [
    "亲爱的，上次你跳过了休息，这次一定要好好休息哦～\n你的健康比任何代码都重要 ❤️",
    "宝贝，你已经连续跳过 {n} 次休息了！\n再不休息我要心疼死了，求求你了好不好 🥺💕",
    "小可爱，你的眼睛和颈椎都在期待这次休息呢～\n别让它们失望哦，我会一直陪着你的 🌟",
    "辛苦了宝！每次看你跳过休息我都好担心～\n这次让身体充充电吧，答应我好吗 💗",
    "你知道吗？你已经跳过 {n} 次休息了……\n世界可以等，但你的身体不能等，休息一下吧亲 😘",
]

CARING_MESSAGE_DESPERATE = (
    "你已经跳过 {n} 次休息了！！！\n"
    "我真的真的好担心你 😭💔\n"
    "拜托了，就休息这一次，好不好？\n"
    "我不想看到你累坏自己……"
)


def get_caring_message(n: int) -> str:
    """根据跳过次数返回肉麻关怀语。"""
    if n <= 0:
        return ""
    if n <= len(CARING_MESSAGES):
        return CARING_MESSAGES[n - 1].format(n=n)
    return CARING_MESSAGE_DESPERATE.format(n=n)


def get_skip_message(n: int) -> str:
    if n <= 0:
        return ""
    if n <= len(SKIP_MESSAGES):
        return SKIP_MESSAGES[n - 1].format(n=n)
    return SKIP_MESSAGE_URGENT.format(n=n)


# ---------------------------------------------------------------------------
# 颜色主题
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#2b2d42",
    "fg": "#edf2f4",
    "accent_work": "#ef233c",
    "accent_rest": "#2ec4b6",
    "accent_idle": "#8d99ae",
    "button_bg": "#3a3d5c",
    "button_active": "#52567a",
    "entry_bg": "#3a3d5c",
    "entry_fg": "#edf2f4",
}


# ---------------------------------------------------------------------------
# 主应用
# ---------------------------------------------------------------------------
class BreakReminderApp:
    """休息提醒小工具主窗口。"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🍅 休息提醒")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        # ---- 状态 ----
        self.state = STATE_IDLE
        self.seconds_left = 0
        self.timer_id = None

        # ---- 统计 ----
        self.rounds_completed = 0
        self.skips_today = 0

        # ---- 默认时长（分钟）----
        self.default_work_min = 45
        self.default_rest_min = 15

        # ---- 暂停前状态 ----
        self._paused_from_state = None

        # ---- 弹窗引用 ----
        self.popup: tk.Toplevel | None = None

        # ---- 构建界面 ----
        self._build_ui()
        self._update_display()

    # ===============================================================
    # UI 构建
    # ===============================================================
    def _build_ui(self):
        pad = {"padx": 16, "pady": 6}

        # -- 状态标签 --
        self.status_var = tk.StringVar(value="⏸ 空闲")
        self.lbl_status = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=COLORS["bg"],
            fg=COLORS["accent_idle"],
            font=("Microsoft YaHei UI", 14, "bold"),
        )
        self.lbl_status.pack(padx=16, pady=(16, 2))

        # -- 倒计时 --
        self.time_var = tk.StringVar(value="00:00")
        self.lbl_time = tk.Label(
            self.root,
            textvariable=self.time_var,
            bg=COLORS["bg"],
            fg=COLORS["fg"],
            font=("Consolas", 48, "bold"),
        )
        self.lbl_time.pack(**pad)

        # -- 设置区域 --
        frm_settings = tk.Frame(self.root, bg=COLORS["bg"])
        frm_settings.pack(**pad)

        tk.Label(frm_settings, text="工作(分钟):", bg=COLORS["bg"], fg=COLORS["fg"],
                 font=("Microsoft YaHei UI", 10)).grid(row=0, column=0, padx=4)
        self.entry_work = tk.Entry(
            frm_settings, width=5, justify="center",
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["entry_fg"],
            font=("Consolas", 12), relief="flat",
        )
        self.entry_work.insert(0, str(self.default_work_min))
        self.entry_work.grid(row=0, column=1, padx=4)

        tk.Label(frm_settings, text="休息(分钟):", bg=COLORS["bg"], fg=COLORS["fg"],
                 font=("Microsoft YaHei UI", 10)).grid(row=0, column=2, padx=(16, 4))
        self.entry_rest = tk.Entry(
            frm_settings, width=5, justify="center",
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["entry_fg"],
            font=("Consolas", 12), relief="flat",
        )
        self.entry_rest.insert(0, str(self.default_rest_min))
        self.entry_rest.grid(row=0, column=3, padx=4)

        # -- 按钮区域 --
        frm_buttons = tk.Frame(self.root, bg=COLORS["bg"])
        frm_buttons.pack(padx=16, pady=(4, 2))

        btn_style = dict(
            bg=COLORS["button_bg"],
            fg=COLORS["fg"],
            activebackground=COLORS["button_active"],
            activeforeground=COLORS["fg"],
            font=("Microsoft YaHei UI", 11),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=6,
        )

        self.btn_start = tk.Button(
            frm_buttons, text="▶ 开始工作", command=self._on_start, **btn_style,
        )
        self.btn_start.grid(row=0, column=0, padx=6)

        self.btn_pause = tk.Button(
            frm_buttons, text="⏸ 暂停", command=self._on_pause, state="disabled", **btn_style,
        )
        self.btn_pause.grid(row=0, column=1, padx=6)

        self.btn_reset = tk.Button(
            frm_buttons, text="⏹ 重置", command=self._on_reset, **btn_style,
        )
        self.btn_reset.grid(row=0, column=2, padx=6)

        self.btn_skip_rest = tk.Button(
            frm_buttons, text="⏭ 跳过休息", command=self._on_skip_rest, **btn_style,
        )
        # 初始隐藏，仅在休息中显示
        self.btn_skip_rest.grid(row=0, column=3, padx=6)
        self.btn_skip_rest.grid_remove()

        # -- 统计区域 --
        frm_stats = tk.Frame(self.root, bg=COLORS["bg"])
        frm_stats.pack(padx=16, pady=(2, 4))

        self.stats_var = tk.StringVar(value="")
        tk.Label(
            frm_stats, textvariable=self.stats_var,
            bg=COLORS["bg"], fg=COLORS["accent_idle"],
            font=("Microsoft YaHei UI", 10),
        ).pack()

        # -- 消息标签（用于鼓励语等）--
        self.msg_var = tk.StringVar(value="")
        self.lbl_msg = tk.Label(
            self.root,
            textvariable=self.msg_var,
            bg=COLORS["bg"],
            fg="#ffd166",
            font=("Microsoft YaHei UI", 9),
            wraplength=360,
        )
        self.lbl_msg.pack(padx=16, pady=(0, 12))

        # -- 窗口居中 --
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"+{x}+{y}")

    # ===============================================================
    # 辅助：读取输入框的分钟数
    # ===============================================================
    def _get_work_minutes(self) -> int:
        try:
            v = int(self.entry_work.get())
            return max(1, v)
        except ValueError:
            return self.default_work_min

    def _get_rest_minutes(self) -> int:
        try:
            v = int(self.entry_rest.get())
            return max(1, v)
        except ValueError:
            return self.default_rest_min

    # ===============================================================
    # 显示更新
    # ===============================================================
    def _update_display(self):
        mins, secs = divmod(max(self.seconds_left, 0), 60)
        self.time_var.set(f"{mins:02d}:{secs:02d}")

        if self.state == STATE_IDLE:
            self.status_var.set("⏸ 空闲")
            self.lbl_status.config(fg=COLORS["accent_idle"])
        elif self.state == STATE_WORKING:
            self.status_var.set("💻 工作中")
            self.lbl_status.config(fg=COLORS["accent_work"])
        elif self.state == STATE_RESTING:
            self.status_var.set("🧘 休息中")
            self.lbl_status.config(fg=COLORS["accent_rest"])
        elif self.state == STATE_PAUSED:
            label = "💻 工作中" if self._paused_from_state == STATE_WORKING else "🧘 休息中"
            self.status_var.set(f"{label} (已暂停)")
            color = COLORS["accent_work"] if self._paused_from_state == STATE_WORKING else COLORS["accent_rest"]
            self.lbl_status.config(fg=color)
        elif self.state == STATE_BREAK_PROMPT:
            self.status_var.set("⏰ 该休息了！")
            self.lbl_status.config(fg="#ffd166")

        self.stats_var.set(
            f"📊 今日统计：已完成 {self.rounds_completed} 轮工作  |  跳过休息 {self.skips_today} 次"
        )

    # ===============================================================
    # 计时器
    # ===============================================================
    def _tick(self):
        if self.state not in (STATE_WORKING, STATE_RESTING):
            return

        self.seconds_left -= 1
        self._update_display()

        if self.seconds_left <= 0:
            if self.state == STATE_WORKING:
                self._on_work_done()
            elif self.state == STATE_RESTING:
                self._on_rest_done()
            return

        self.timer_id = self.root.after(1000, self._tick)

    def _cancel_timer(self):
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    # ===============================================================
    # 按钮事件
    # ===============================================================
    def _on_start(self):
        if self.state != STATE_IDLE:
            return
        self._start_work()

    def _on_pause(self):
        if self.state == STATE_PAUSED:
            # 恢复
            self.state = self._paused_from_state
            self._paused_from_state = None
            self.btn_pause.config(text="⏸ 暂停")
            self.btn_start.config(state="disabled")
            self._update_display()
            self.timer_id = self.root.after(1000, self._tick)
        elif self.state in (STATE_WORKING, STATE_RESTING):
            self._cancel_timer()
            self._paused_from_state = self.state
            self.state = STATE_PAUSED
            self.btn_pause.config(text="▶ 继续")
            self._update_display()

    def _on_skip_rest(self):
        """休息中跳过休息 → 计入跳过次数，直接开始工作。"""
        if self.state != STATE_RESTING:
            return
        self._cancel_timer()
        self.skips_today += 1
        msg = get_skip_message(self.skips_today)
        self.msg_var.set(msg)
        self._start_work()

    def _on_reset(self):
        self._cancel_timer()
        self._close_popup()
        self.state = STATE_IDLE
        self.seconds_left = 0
        self.msg_var.set("")
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸ 暂停")
        self.btn_skip_rest.grid_remove()
        self._update_display()

    # ===============================================================
    # 工作 / 休息流程
    # ===============================================================
    def _start_work(self):
        self._close_popup()
        self.state = STATE_WORKING
        self.seconds_left = self._get_work_minutes() * 60
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal", text="⏸ 暂停")
        self.btn_skip_rest.grid_remove()
        self.msg_var.set("")
        self._update_display()
        self.timer_id = self.root.after(1000, self._tick)

    def _start_rest(self):
        self._close_popup()
        self.state = STATE_RESTING
        self.seconds_left = self._get_rest_minutes() * 60
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal", text="⏸ 暂停")
        self.btn_skip_rest.grid()
        self.msg_var.set("")
        self._update_display()
        self.timer_id = self.root.after(1000, self._tick)

    def _on_work_done(self):
        """工作时间结束 → 弹窗提醒。"""
        self._cancel_timer()
        self.rounds_completed += 1
        self.state = STATE_BREAK_PROMPT
        self._update_display()
        play_alert_sound()
        self._show_break_prompt()

    def _on_rest_done(self):
        """休息时间结束 → 弹窗提醒并自动开始下一轮工作。"""
        self._cancel_timer()
        self.state = STATE_IDLE
        self._update_display()
        play_alert_sound()
        self._show_rest_done_popup()

    # ===============================================================
    # 弹窗：工作结束提醒
    # ===============================================================
    def _show_break_prompt(self):
        self._close_popup()

        popup = tk.Toplevel(self.root)
        popup.title("⏰ 休息时间到！")
        popup.configure(bg=COLORS["bg"])
        popup.resizable(False, False)
        popup.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁止关闭

        # 强制置顶
        popup.attributes("-topmost", True)
        popup.lift()
        popup.focus_force()

        tk.Label(
            popup, text="⏰", bg=COLORS["bg"], font=("Segoe UI Emoji", 48),
        ).pack(pady=(20, 4))

        tk.Label(
            popup,
            text=f"你已经连续工作了 {self._get_work_minutes()} 分钟！\n站起来活动一下吧～",
            bg=COLORS["bg"], fg=COLORS["fg"],
            font=("Microsoft YaHei UI", 13),
            justify="center",
        ).pack(padx=30, pady=8)

        # 如果之前跳过过休息，显示肉麻关怀语
        if self.skips_today > 0:
            caring_msg = get_caring_message(self.skips_today)
            tk.Label(
                popup,
                text=caring_msg,
                bg=COLORS["bg"], fg="#ff9eb5",
                font=("Microsoft YaHei UI", 11),
                justify="center",
                wraplength=350,
            ).pack(padx=30, pady=(0, 8))

        frm = tk.Frame(popup, bg=COLORS["bg"])
        frm.pack(pady=(8, 20))

        btn_style = dict(
            fg=COLORS["fg"],
            activeforeground=COLORS["fg"],
            font=("Microsoft YaHei UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
        )

        tk.Button(
            frm, text="🧘 立即休息",
            bg=COLORS["accent_rest"],
            activebackground="#26a69a",
            command=lambda: self._popup_rest(popup),
            **btn_style,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            frm, text="💪 继续工作",
            bg=COLORS["accent_work"],
            activebackground="#c62828",
            command=lambda: self._popup_skip(popup),
            **btn_style,
        ).grid(row=0, column=1, padx=10)

        self.popup = popup
        self._center_popup(popup)

    def _popup_rest(self, popup: tk.Toplevel):
        popup.destroy()
        self.popup = None
        self._start_rest()

    def _popup_skip(self, popup: tk.Toplevel):
        self.skips_today += 1
        popup.destroy()
        self.popup = None
        msg = get_skip_message(self.skips_today)
        self.msg_var.set(msg)
        self._start_work()

    # ===============================================================
    # 弹窗：休息结束提醒
    # ===============================================================
    def _show_rest_done_popup(self):
        self._close_popup()

        popup = tk.Toplevel(self.root)
        popup.title("✅ 休息结束")
        popup.configure(bg=COLORS["bg"])
        popup.resizable(False, False)

        popup.attributes("-topmost", True)
        popup.lift()
        popup.focus_force()

        tk.Label(
            popup, text="✅", bg=COLORS["bg"], font=("Segoe UI Emoji", 48),
        ).pack(pady=(20, 4))

        tk.Label(
            popup,
            text="休息结束啦！\n精神满满，继续加油 💪",
            bg=COLORS["bg"], fg=COLORS["fg"],
            font=("Microsoft YaHei UI", 13),
            justify="center",
        ).pack(padx=30, pady=8)

        btn_style = dict(
            fg=COLORS["fg"],
            activeforeground=COLORS["fg"],
            font=("Microsoft YaHei UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
        )

        tk.Button(
            popup, text="▶ 开始工作",
            bg=COLORS["accent_rest"],
            activebackground="#26a69a",
            command=lambda: self._popup_start_work(popup),
            **btn_style,
        ).pack(pady=(8, 20))

        self.popup = popup
        self._center_popup(popup)

    def _popup_start_work(self, popup: tk.Toplevel):
        popup.destroy()
        self.popup = None
        self._start_work()

    # ===============================================================
    # 弹窗辅助
    # ===============================================================
    def _close_popup(self):
        if self.popup is not None:
            try:
                self.popup.destroy()
            except tk.TclError:
                pass
            self.popup = None

    @staticmethod
    def _center_popup(popup: tk.Toplevel):
        popup.update_idletasks()
        w = popup.winfo_width()
        h = popup.winfo_height()
        x = (popup.winfo_screenwidth() - w) // 2
        y = (popup.winfo_screenheight() - h) // 2
        popup.geometry(f"+{x}+{y}")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()

    # 高 DPI 适配 (Windows)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = BreakReminderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
