import json
import math
import os
import queue
import threading
import time
import uuid
import tkinter as tk
from tkinter import messagebox


class NovaUI:
    """Full-size ChatGPT-inspired desktop interface for Nova.

    Public interface used by main.py:
      ui.set_state("idle" | "listening" | "speaking")
      ui.set_status(text)
      ui.add_message("You" | "Nova", text)
      ui.input_queue.get(...)
      ui.voice_requested.wait(...)
      ui.stop_event.is_set()
      ui.shutdown()

    Chat history is saved locally in data/nova_chats.json.
    """

    BG = "#212121"
    SIDEBAR = "#171717"
    PANEL = "#262626"
    PANEL_HOVER = "#303030"
    TEXT = "#ECECEC"
    MUTED = "#A0A0A0"
    ACCENT = "#27C5F5"
    USER_BUBBLE = "#303030"
    NOVA_BUBBLE = "#252525"

    def __init__(self):
        self.commands = queue.Queue()
        self.input_queue = queue.Queue()
        self.voice_requested = threading.Event()
        self.stop_event = threading.Event()
        self.closed_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def set_state(self, state):
        self.commands.put(("state", state))

    def set_status(self, text):
        self.commands.put(("status", str(text)))

    def add_message(self, role, text):
        self.commands.put(("message", str(role), str(text)))

    def shutdown(self, wait=True):
        self.commands.put(("shutdown", None))
        if wait:
            self.closed_event.wait(timeout=3)

    def _run(self):
        root = tk.Tk()
        root.title("Nova AI")
        root.geometry("1180x760")
        root.minsize(850, 600)
        root.configure(bg=self.BG)

        try:
            root.iconname("Nova AI")
        except tk.TclError:
            pass

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.history_path = os.path.join(data_dir, "nova_chats.json")
        self.history = self._load_history()
        self.active_chat_id = None
        self.state = "idle"
        self.status_text = "Ready when you are"
        self._closing = False
        self._bubble_widgets = []

        self._build_layout(root)
        self._refresh_chat_list()

        if self.history:
            self._select_chat(self.history[0]["id"])
        else:
            self._new_chat()

        def process_commands():
            while True:
                try:
                    item = self.commands.get_nowait()
                except queue.Empty:
                    break

                action = item[0]
                if action == "state":
                    self.state = item[1]
                    self._update_status_from_state()
                elif action == "status":
                    self.status_text = item[1]
                    self._update_status_label()
                elif action == "message":
                    self._append_message(item[1], item[2])
                elif action == "shutdown":
                    self._closing = True
                    self.stop_event.set()
                    root.destroy()
                    self.closed_event.set()
                    return

            if self.stop_event.is_set() and not self._closing:
                self._closing = True
                root.destroy()
                self.closed_event.set()
                return
            root.after(40, process_commands)

        def on_close():
            self.stop_event.set()
            self.voice_requested.clear()
            self._save_history()
            self._closing = True
            root.destroy()
            self.closed_event.set()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.bind("<Escape>", lambda _event: on_close())
        process_commands()
        root.mainloop()
        self.closed_event.set()

    def _load_history(self):
        try:
            with open(self.history_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                valid = []
                for chat in data:
                    if isinstance(chat, dict) and "id" in chat and isinstance(chat.get("messages"), list):
                        chat.setdefault("title", "New chat")
                        chat.setdefault("updated", time.time())
                        valid.append(chat)
                return sorted(valid, key=lambda item: item.get("updated", 0), reverse=True)
        except (OSError, json.JSONDecodeError, TypeError):
            pass
        return []

    def _save_history(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as file:
                json.dump(self.history, file, ensure_ascii=False, indent=2)
        except OSError as error:
            print("Could not save Nova chat history:", error)

    def _build_layout(self, root):
        self.root = root
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Left sidebar
        self.sidebar = tk.Frame(root, bg=self.SIDEBAR, width=265)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(4, weight=1)

        brand = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        brand.pack(fill="x", padx=18, pady=(18, 16))
        tk.Label(brand, text="✦", fg=self.ACCENT, bg=self.SIDEBAR,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(brand, text="  NOVA AI", fg=self.TEXT, bg=self.SIDEBAR,
                 font=("Segoe UI Semibold", 15)).pack(side="left", pady=(3, 0))

        self._sidebar_button(self.sidebar, "+  New chat", self._new_chat, accent=True).pack(
            fill="x", padx=12, pady=(0, 8), ipady=7)

        self.search_var = tk.StringVar()
        search = tk.Entry(self.sidebar, textvariable=self.search_var,
                          bg=self.PANEL, fg=self.TEXT, insertbackground=self.TEXT,
                          relief="flat", font=("Segoe UI", 10))
        search.pack(fill="x", padx=12, pady=(0, 14), ipady=8)
        search.insert(0, "Search chats...")
        search.configure(fg=self.MUTED)
        search.bind("<FocusIn>", self._search_focus_in)
        search.bind("<FocusOut>", self._search_focus_out)
        self.search_var.trace_add("write", lambda *_: self._refresh_chat_list())
        self.search_entry = search

        tk.Label(self.sidebar, text="RECENTS", fg=self.MUTED, bg=self.SIDEBAR,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(
            fill="x", padx=18, pady=(0, 7))

        self.chat_list = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        self.chat_list.pack(fill="both", expand=True, padx=8)

        footer = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        footer.pack(side="bottom", fill="x", padx=14, pady=14)
        tk.Label(footer, text="●  LOCAL CHAT HISTORY", fg="#76D6A6", bg=self.SIDEBAR,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(footer, text="Saved on this computer", fg=self.MUTED, bg=self.SIDEBAR,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        # Main conversation panel
        self.main_panel = tk.Frame(root, bg=self.BG)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_rowconfigure(1, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        topbar = tk.Frame(self.main_panel, bg=self.BG, height=62)
        topbar.grid(row=0, column=0, sticky="ew", padx=28, pady=(10, 0))
        topbar.grid_columnconfigure(0, weight=1)
        tk.Label(topbar, text="Nova", fg=self.TEXT, bg=self.BG,
                 font=("Segoe UI Semibold", 14)).grid(row=0, column=0, sticky="w")
        self.state_dot = tk.Label(topbar, text="●", fg=self.ACCENT, bg=self.BG,
                                  font=("Segoe UI", 10))
        self.state_dot.grid(row=0, column=1, padx=(0, 7))
        self.status_label = tk.Label(topbar, text=self.status_text, fg=self.MUTED, bg=self.BG,
                                     font=("Segoe UI", 9))
        self.status_label.grid(row=0, column=2, sticky="e")

        self.chat_area = tk.Frame(self.main_panel, bg=self.BG)
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=28)
        self.chat_area.grid_rowconfigure(0, weight=1)
        self.chat_area.grid_columnconfigure(0, weight=1)

        self.chat_canvas = tk.Canvas(self.chat_area, bg=self.BG, highlightthickness=0, bd=0)
        self.chat_scroll = tk.Scrollbar(self.chat_area, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        self.chat_scroll.grid(row=0, column=1, sticky="ns")
        self.messages_frame = tk.Frame(self.chat_canvas, bg=self.BG)
        self.messages_window = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.messages_frame.bind("<Configure>", self._on_messages_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Bottom composer
        composer_wrap = tk.Frame(self.main_panel, bg=self.BG)
        composer_wrap.grid(row=2, column=0, sticky="ew", padx=28, pady=(14, 20))
        composer_wrap.grid_columnconfigure(0, weight=1)

        composer = tk.Frame(composer_wrap, bg=self.PANEL, highlightthickness=1,
                            highlightbackground="#3B3B3B")
        composer.grid(row=0, column=0, sticky="ew")
        composer.grid_columnconfigure(0, weight=1)
        self.input_text = tk.Text(composer, height=2, wrap="word", bg=self.PANEL,
                                  fg=self.TEXT, insertbackground=self.TEXT,
                                  relief="flat", bd=0, padx=15, pady=13,
                                  font=("Segoe UI", 11), undo=True)
        self.input_text.grid(row=0, column=0, sticky="nsew")
        self.input_text.insert("1.0", "Message Nova...")
        self.input_text.configure(fg="#888888")
        self.input_text.bind("<FocusIn>", self._composer_focus_in)
        self.input_text.bind("<FocusOut>", self._composer_focus_out)
        self.input_text.bind("<Return>", self._on_enter)

        buttons = tk.Frame(composer, bg=self.PANEL)
        buttons.grid(row=0, column=1, sticky="se", padx=(0, 9), pady=8)
        self.mic_button = tk.Button(buttons, text="🎙", command=self._request_voice,
                                    bg="#383838", fg=self.TEXT, activebackground="#454545",
                                    activeforeground=self.TEXT, relief="flat", bd=0,
                                    font=("Segoe UI Emoji", 13), cursor="hand2", width=3)
        self.mic_button.pack(side="left", padx=(0, 7), ipady=4)
        self.send_button = tk.Button(buttons, text="↑", command=self._submit_message,
                                     bg=self.ACCENT, fg="#06131A", activebackground="#70DDFB",
                                     activeforeground="#06131A", relief="flat", bd=0,
                                     font=("Segoe UI", 16, "bold"), cursor="hand2", width=3)
        self.send_button.pack(side="left", ipady=1)

        tk.Label(composer_wrap,
                 text="Nova can make mistakes. Check important information before acting.",
                 fg="#777777", bg=self.BG, font=("Segoe UI", 8)).grid(
            row=1, column=0, pady=(8, 0))

    def _sidebar_button(self, parent, text, command, accent=False):
        bg = "#15394A" if accent else self.SIDEBAR
        fg = "#BDEFFF" if accent else self.TEXT
        return tk.Button(parent, text=text, command=command, anchor="w",
                         bg=bg, fg=fg, activebackground=self.PANEL_HOVER,
                         activeforeground=self.TEXT, relief="flat", bd=0,
                         padx=13, font=("Segoe UI", 10), cursor="hand2")

    def _search_focus_in(self, _event=None):
        if self.search_entry.get() == "Search chats...":
            self.search_entry.delete(0, "end")
            self.search_entry.configure(fg=self.TEXT)

    def _search_focus_out(self, _event=None):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search chats...")
            self.search_entry.configure(fg=self.MUTED)

    def _composer_focus_in(self, _event=None):
        if self.input_text.get("1.0", "end-1c") == "Message Nova...":
            self.input_text.delete("1.0", "end")
            self.input_text.configure(fg=self.TEXT)

    def _composer_focus_out(self, _event=None):
        if not self.input_text.get("1.0", "end-1c").strip():
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", "Message Nova...")
            self.input_text.configure(fg="#888888")

    def _on_enter(self, event):
        if event.state & 0x0001:  # Shift+Enter inserts a new line.
            return None
        self._submit_message()
        return "break"

    def _submit_message(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text or text == "Message Nova...":
            return
        self.input_text.delete("1.0", "end")
        self.input_text.configure(fg=self.TEXT)
        self._append_message("You", text)
        self.input_queue.put(text)
        self._set_status("Processing your message...")
        self.input_text.focus_set()

    def _request_voice(self):
        if self.stop_event.is_set():
            return
        self.voice_requested.set()
        self._set_status("Microphone requested — speak after Nova starts listening")
        self.mic_button.configure(bg="#075B78", fg="#FFFFFF")
        self.root.after(1500, lambda: self.mic_button.configure(bg="#383838", fg=self.TEXT))

    def _new_chat(self):
        chat = {
            "id": uuid.uuid4().hex,
            "title": "New chat",
            "updated": time.time(),
            "messages": []
        }
        self.history.insert(0, chat)
        self.active_chat_id = chat["id"]
        self._save_history()
        self._refresh_chat_list()
        self._render_active_chat()
        self.input_text.focus_set()

    def _active_chat(self):
        for chat in self.history:
            if chat.get("id") == self.active_chat_id:
                return chat
        return None

    def _select_chat(self, chat_id):
        self.active_chat_id = chat_id
        self._render_active_chat()
        self._refresh_chat_list()

    def _refresh_chat_list(self):
        for child in self.chat_list.winfo_children():
            child.destroy()
        query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        if query == "search chats...":
            query = ""
        visible = [chat for chat in sorted(self.history, key=lambda item: item.get("updated", 0), reverse=True)
                   if query in chat.get("title", "").lower()]
        if not visible:
            tk.Label(self.chat_list, text="No matching chats", fg=self.MUTED,
                     bg=self.SIDEBAR, font=("Segoe UI", 9)).pack(anchor="w", padx=10, pady=8)
            return
        for chat in visible[:80]:
            is_active = chat.get("id") == self.active_chat_id
            btn = tk.Button(self.chat_list, text="  " + chat.get("title", "New chat"),
                            command=lambda cid=chat["id"]: self._select_chat(cid),
                            anchor="w", bg="#343434" if is_active else self.SIDEBAR,
                            fg=self.TEXT, activebackground=self.PANEL_HOVER,
                            activeforeground=self.TEXT, relief="flat", bd=0,
                            font=("Segoe UI", 9), cursor="hand2")
            btn.pack(fill="x", pady=2, ipady=7)

    def _render_active_chat(self):
        for child in self.messages_frame.winfo_children():
            child.destroy()
        chat = self._active_chat()
        if not chat or not chat.get("messages"):
            welcome = tk.Frame(self.messages_frame, bg=self.BG)
            welcome.pack(fill="x", pady=(120, 20))
            tk.Label(welcome, text="✦", fg=self.ACCENT, bg=self.BG,
                     font=("Segoe UI", 30, "bold")).pack()
            tk.Label(welcome, text="How can I help you today?", fg=self.TEXT, bg=self.BG,
                     font=("Segoe UI Semibold", 20)).pack(pady=(8, 7))
            tk.Label(welcome, text="Ask a question, type a command, or use the microphone.",
                     fg=self.MUTED, bg=self.BG, font=("Segoe UI", 10)).pack()
        else:
            for item in chat["messages"]:
                self._draw_message(item.get("role", "Nova"), item.get("text", ""))
        self.root.after(60, self._scroll_to_bottom)

    def _append_message(self, role, text):
        chat = self._active_chat()
        if chat is None:
            self._new_chat()
            chat = self._active_chat()
        message = {"role": role, "text": str(text), "time": time.time()}
        chat["messages"].append(message)
        chat["updated"] = time.time()
        if role == "You" and chat.get("title") == "New chat":
            title = " ".join(str(text).split())
            chat["title"] = title[:36] + ("…" if len(title) > 36 else "") or "New chat"
        self._save_history()
        self._refresh_chat_list()
        self._draw_message(role, str(text))
        self._scroll_to_bottom()

    def _draw_message(self, role, text):
        row = tk.Frame(self.messages_frame, bg=self.BG)
        row.pack(fill="x", pady=(8, 8), padx=10)
        is_user = role.lower() in ("you", "user")
        if is_user:
            holder = tk.Frame(row, bg=self.USER_BUBBLE)
            holder.pack(side="right", anchor="e")
        else:
            holder = tk.Frame(row, bg=self.NOVA_BUBBLE)
            holder.pack(side="left", anchor="w")

        label_text = "You" if is_user else "✦  Nova"
        tk.Label(holder, text=label_text,
                 fg=self.ACCENT if not is_user else "#D6D6D6",
                 bg=holder["bg"], font=("Segoe UI Semibold", 9),
                 anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        tk.Label(holder, text=text, fg=self.TEXT, bg=holder["bg"],
                 font=("Segoe UI", 10), justify="left", anchor="w",
                 wraplength=650, padx=14, pady=2).pack(fill="x", pady=(0, 9))

    def _on_messages_configure(self, _event=None):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.chat_canvas.itemconfigure(self.messages_window, width=event.width)

    def _on_mousewheel(self, event):
        try:
            if self.chat_canvas.winfo_exists():
                self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

    def _scroll_to_bottom(self):
        try:
            self.chat_canvas.update_idletasks()
            self.chat_canvas.yview_moveto(1.0)
        except tk.TclError:
            pass

    def _set_status(self, text):
        self.status_text = text
        self._update_status_label()

    def _update_status_from_state(self):
        if self.state == "listening":
            self.status_text = "Listening…"
            self.state_dot.configure(fg="#F0B34B")
        elif self.state == "speaking":
            self.status_text = "Speaking…"
            self.state_dot.configure(fg=self.ACCENT)
        else:
            self.status_text = "Ready when you are"
            self.state_dot.configure(fg="#76D6A6")
        self._update_status_label()

    def _update_status_label(self):
        try:
            self.status_label.configure(text=self.status_text)
        except tk.TclError:
            pass


if __name__ == "__main__":
    app = NovaUI()
    app.thread.join()
