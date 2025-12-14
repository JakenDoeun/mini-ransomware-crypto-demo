import customtkinter as ctk
import json
import os
import threading
import time
import sys
import random
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

DATA_FILE = "access_data.json"
ACCESS_DAYS = 1

#store first run date or load existing
def load_or_create_access_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return datetime.fromisoformat(json.load(f)["first_run"])
    else:
        now = datetime.now()
        with open(DATA_FILE, "w") as f:
            json.dump({"first_run": now.isoformat()}, f)
        return now


class Ransom_UI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SYSTEM ACCESS REQUIRED")
        self.geometry("700x500")
        self.resizable(False, False)

        self.first_run = load_or_create_access_data()
        self.expire_date = self.first_run + timedelta(days=ACCESS_DAYS)

        #colors ref
        self.neon = "#14ff00"
        self.dark_green = "#0A9900"
        self.alert_red = "#ff0033"
        self.panel_bg = "#001a00"
        self.desc_base_text = "Your device has been locked.\nPAY US to get the KEY"
        ascii_art = r"""
░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░  
"""
        self.ascii_label = ctk.CTkLabel(
            self,
            text=ascii_art,
            font=("Consolas", 14),
            text_color=self.neon
        )
        self.ascii_label.pack(pady=5)

      
        #main frame
        self.frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#001800")
        self.frame.pack(padx=20, pady=15, fill="both", expand=True)

       #description label with blinking cursor

        self.desc = ctk.CTkLabel(
            self.frame,
            text=self.desc_base_text + " █",
            font=("Consolas", 15),
            text_color=self.dark_green,
            justify="center"
        )
        self.desc.pack(pady=(15, 10))

        # Start Linux-style block cursor blink
        threading.Thread(target=self.blink_block_cursor, daemon=True).start()
        
        #copyable function
        self.example_frame = ctk.CTkFrame(self.frame, fg_color="#001800")
        self.example_frame.pack(pady=(0, 10))

        self.example_label = ctk.CTkLabel(
            self.example_frame,
            text="Bitcoin address:",
            font=("Consolas", 13),
            text_color=self.dark_green
        )
        self.example_label.grid(row=0, column=0, padx=5)

        self.Key_code = "ACCESS-GRANTED" #Network address of crypto

        self.code_display = ctk.CTkLabel(
            self.example_frame,
            text=self.Key_code,
            font=("Consolas", 13, "bold"),
            text_color=self.neon
        )
        self.code_display.grid(row=0, column=1, padx=5)

        self.copy_btn = ctk.CTkButton(
            self.example_frame,
            text="📋 COPY",
            width=70,
            height=26,
            fg_color=self.dark_green,
            hover_color=self.neon,
            text_color="black",
            command=self.copy_Key_code
        )
        self.copy_btn.grid(row=0, column=2, padx=5)

    
        #timer display
        self.timer_label = ctk.CTkLabel(
            self.frame,
            text="Loading timer...",
            font=("Consolas", 18, "bold"),
            text_color=self.neon
        )
        self.timer_label.pack(pady=5)

    
        #input placeholder entry
        self.entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="ENTER ACCESS CODE...",
            fg_color="#002800",
            text_color=self.neon,
            placeholder_text_color="#158015"
        )
        self.entry.pack(pady=10, padx=20, fill="x")

    
        #verify button
        self.btn = ctk.CTkButton(
            self.frame,
            text="VERIFY CODE",
            fg_color=self.dark_green,
            hover_color=self.neon,
            text_color="black",
            command=self.verify_code
        )
        self.btn.pack(pady=10)

        threading.Thread(target=self.update_timer, daemon=True).start()

    #blink block cursor
    def blink_block_cursor(self):
        visible = True
        while True:
            if visible:
                self.desc.configure(text=self.desc_base_text + "█")
            else:
                self.desc.configure(text=self.desc_base_text + " ")
            visible = not visible
            time.sleep(0.6)

    #copy 
    def copy_Key_code(self):
        self.clipboard_clear()
        self.clipboard_append(self.Key_code)
        self.copy_btn.configure(text="COPIED ✓")
        self.after(1000, lambda: self.copy_btn.configure(text="COPY"))

    
    #GLITCH EFFECT
    def glitch_effect(self):
        original = "INVALID KEY ✖"
        chars = "!@#$%^&*()<>?/[]{}|▓▒░"

        for _ in range(15):
            scrambled = "".join(
                random.choice(chars) if random.random() < 0.35 else c
                for c in original
            )
            self.timer_label.configure(text=scrambled, text_color=self.alert_red)
            time.sleep(0.04)

        self.timer_label.configure(text=original, text_color=self.alert_red)
    

    #verify key
    def verify_code(self):
        if self.entry.get().strip() == "ACCESS-GRANTED":
            self.timer_label.configure(text="ACCESS APPROVED ✓", text_color="#00ff44")
            self.after(1500, self.destroy)
        else:
            threading.Thread(target=self.glitch_effect, daemon=True).start()

    #tracking time left
    def update_timer(self):
        while True:
            now = datetime.now()
            remaining = self.expire_date - now

            if remaining.total_seconds() <= 0:
                self.timer_label.configure(text="TIMEOUT ❌, Your key is no longer existing.", text_color=self.alert_red)
                time.sleep(1)
                sys.exit("ACCESS TIME EXPIRED")
            elif remaining.total_seconds() < 3600:
                self.timer_label.configure(text_color=self.alert_red)
    
            d = remaining.days
            h, r = divmod(remaining.seconds, 3600)
            m, s = divmod(r, 60)

            self.timer_label.configure(
                text=f"TIME LEFT: {d}d {h}h {m}m {s}s",
                text_color=self.neon
            )
            time.sleep(1)


if __name__ == "__main__":
    app = Ransom_UI()
    app.mainloop()
