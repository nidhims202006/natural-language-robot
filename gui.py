"""
gui.py
The control panel window — a separate GUI that runs alongside
the 3D simulation, letting you type natural language commands.

Uses tkinter — which is built into Python, no install needed.
Runs in its own thread so the simulation never freezes.
"""
import tkinter as tk
from tkinter import scrolledtext
import queue
import threading


class ControlPanel:
    def __init__(self, command_queue: queue.Queue):
        self.command_queue = command_queue
        self.root    = None
        self.thread  = None
        self.history = []
        self.hist_idx = -1

    def start(self):
        """Launch the GUI in a background thread."""
        self.thread = threading.Thread(target=self._build, daemon=True)
        self.thread.start()

    def _build(self):
        self.root = tk.Tk()
        self.root.title("🤖 Robot Brain — Natural Language Control")
        self.root.geometry("540x620")
        self.root.configure(bg="#0f0f1a")
        self.root.resizable(True, True)

        # ── Title ─────────────────────────────────────────────────────────────
        tk.Label(self.root, text="🤖  Natural Language Robot Control",
                  font=("Segoe UI", 13, "bold"),
                  bg="#0f0f1a", fg="#c8d0ff").pack(pady=(14, 2))
        tk.Label(self.root,
                  text="Type plain English to control the arm below",
                  font=("Segoe UI", 9), bg="#0f0f1a", fg="#666").pack(pady=(0, 12))

        # ── Log window ────────────────────────────────────────────────────────
        tk.Label(self.root, text="Log:", font=("Segoe UI", 9, "bold"),
                  bg="#0f0f1a", fg="#8888bb").pack(padx=14, anchor="w")

        self.log = scrolledtext.ScrolledText(
            self.root, height=14,
            font=("Consolas", 9),
            bg="#090912", fg="#5ba3f5",
            insertbackground="white",
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.log.pack(padx=14, pady=(4, 10), fill=tk.BOTH, expand=True)

        # ── Quick command buttons ─────────────────────────────────────────────
        tk.Label(self.root, text="Quick Commands:",
                  font=("Segoe UI", 9, "bold"),
                  bg="#0f0f1a", fg="#8888bb").pack(padx=14, anchor="w")

        btn_frame = tk.Frame(self.root, bg="#0f0f1a")
        btn_frame.pack(padx=14, pady=(4, 10), fill=tk.X)

        quick = [
            ("🏠 Home",              "go home"),
            ("📦 Pick Red Cube",     "pick up the red cube"),
            ("↔️  Swap Red & Blue",  "pick up the red cube and place it left of the blue cube"),
            ("🔵 Stack on Red",      "place the blue cube on top of the red cube"),
        ]
        for idx, (label, cmd) in enumerate(quick):
            tk.Button(
                btn_frame, text=label,
                command=lambda c=cmd: self._quick(c),
                font=("Segoe UI", 9),
                bg="#161630", fg="#d0d8ff",
                activebackground="#1e1e55",
                relief="flat", padx=8, pady=5, cursor="hand2"
            ).grid(row=idx // 2, column=idx % 2, padx=3, pady=3, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # ── Text input ────────────────────────────────────────────────────────
        tk.Label(self.root, text="Your command:",
                  font=("Segoe UI", 9, "bold"),
                  bg="#0f0f1a", fg="#8888bb").pack(padx=14, anchor="w")

        row = tk.Frame(self.root, bg="#0f0f1a")
        row.pack(padx=14, pady=(4, 14), fill=tk.X)

        self.entry = tk.Entry(row, font=("Segoe UI", 11),
                               bg="#090912", fg="#ffffff",
                               insertbackground="white",
                               relief="flat", bd=6)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry.bind("<Return>",  lambda e: self._send())
        self.entry.bind("<Up>",      self._hist_up)
        self.entry.bind("<Down>",    self._hist_down)
        self.entry.focus()

        tk.Button(row, text="Send ▶",
                   command=self._send,
                   font=("Segoe UI", 10, "bold"),
                   bg="#1a3a70", fg="white",
                   activebackground="#1e4d99",
                   relief="flat", padx=14, pady=5,
                   cursor="hand2").pack(side=tk.RIGHT)

        # ── Status bar ────────────────────────────────────────────────────────
        self._status = tk.StringVar(value="● Ready")
        tk.Label(self.root, textvariable=self._status,
                  font=("Segoe UI", 9),
                  bg="#070710", fg="#5ba3f5",
                  anchor="w", padx=10
                  ).pack(fill=tk.X, side=tk.BOTTOM)

        # Welcome
        self._log("🤖 Control Panel ready!")
        self._log("💡 Try: 'pick up the red cube and place it left of the blue cube'")
        self._log("💡 Try: 'go home' to reset the arm")
        self._log("─" * 46)

        self.root.mainloop()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _send(self):
        cmd = self.entry.get().strip()
        if not cmd:
            return
        self._log(f"\n👤 You: {cmd}")
        self.command_queue.put(("command", cmd))
        self.history.append(cmd)
        self.hist_idx = -1
        self.entry.delete(0, tk.END)
        self.set_status("⏳ Processing…")

    def _quick(self, cmd):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, cmd)
        self._send()

    def _hist_up(self, _):
        if self.history and self.hist_idx < len(self.history) - 1:
            self.hist_idx += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[-(self.hist_idx + 1)])

    def _hist_down(self, _):
        if self.hist_idx > 0:
            self.hist_idx -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[-(self.hist_idx + 1)])
        elif self.hist_idx == 0:
            self.hist_idx = -1
            self.entry.delete(0, tk.END)

    def _log(self, msg):
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    # ── Public methods (called from main thread) ───────────────────────────────

    def log(self, msg):
        """Thread-safe log update."""
        if self.root and self.root.winfo_exists():
            self.root.after(0, lambda: self._log(msg))

    def set_status(self, msg):
        """Thread-safe status bar update."""
        if self.root and self.root.winfo_exists():
            self.root.after(0, lambda: self._status.set(msg))