##TODO:
# 2. examples: https://github.com/TomSchimansky/CustomTkinter/tree/master/examples
# 3. docs: https://customtkinter.tomschimansky.com/documentation/
# 16. put ffmpeg folder inside _internal and then in installer add path to this folder, but ask user if they want it
# 18. if ffmpef or yt-dlp not found raise error and print it

import os
import customtkinter
from PIL import Image
import json
from pathlib import Path
import jsonpickle
import downloader as BerriedDL
import threading


# ---------------------------------------------------------------------------- #
#                                    Consts                                    #
# ---------------------------------------------------------------------------- #
PATH_ROOT = os.path.dirname(os.path.realpath(__file__))
PATH_CONFIG = os.path.join(PATH_ROOT, "config")
Path(PATH_CONFIG).mkdir(parents=True, exist_ok=True) # create folder if didn't exist already

RADIO_NAMES = ['Video', 'Only Audio', 'Both Types']
LABEL_NAMES = ['YouTube URL:', 'Media Type:', 'Download Path:']


# ---------------------------------------------------------------------------- #
#                                     Theme                                    #
# ---------------------------------------------------------------------------- #

#customtkinter.set_default_color_theme("green")
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme(os.path.join(PATH_CONFIG, "custom_theme.json"))


# ---------------------------------------------------------------------------- #
#                            Frame for all settings                            #
# ---------------------------------------------------------------------------- #
class Settings():
    def __init__(self):
        # default values
        self.radio_state = customtkinter.StringVar(value=RADIO_NAMES[0])
        if os.path.basename(PATH_ROOT) == 'Data':
            self.dlpath = os.path.join(os.path.dirname(PATH_ROOT), "downloads")
        else:
            self.dlpath = os.path.join(PATH_ROOT, "downloads")

        # load json
        settings_path = os.path.join(PATH_CONFIG, "settings.json")
        if (Path(settings_path).is_file()):
            with open(settings_path, "r") as file:
                data = json.load(file)
            obj = jsonpickle.decode(data)
            self.radio_state = customtkinter.StringVar(value=obj.radio_state)
            self.dlpath = obj.dlpath
    
    def preJSON(self):
        self.radio_state = self.radio_state.get()


class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Values
        self.settings = Settings()
        self.radios = RADIO_NAMES
        self.labels = LABEL_NAMES
        self.radiobuttons = []

        # Main Frame Grid 3x2
        self.grid_columnconfigure(1, weight=1)

        # Labels
        for i, value in enumerate(self.labels):
            label = customtkinter.CTkLabel(self, text=value)
            label.grid(row=i, column=0, padx=20, pady=20, sticky="w")

        # Entry
        self.entry_field = customtkinter.CTkEntry(self, placeholder_text="https://www.youtube.com/", width=5000)
        self.entry_field.grid(row=0, column=1, padx=20, pady=20, sticky="w")

        # Radiobuttons
        buttons_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        buttons_frame.grid(row=1, column=1, sticky="w")
        
        for i, value in enumerate(self.radios):
            radiobutton = customtkinter.CTkRadioButton(buttons_frame, text=value, value=value, variable=self.settings.radio_state)
            radiobutton.grid(row=0, column=i, padx=20, pady=20, sticky="ws")
            self.radiobuttons.append(radiobutton)
        
        # Browse
        browse_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        browse_frame.grid(row=2, column=1, sticky="w")
        browse_frame.grid_columnconfigure(0, weight=1)

        self.entry_browse = customtkinter.CTkEntry(browse_frame, textvariable=customtkinter.StringVar(value=self.settings.dlpath), width=5000)
        self.entry_browse.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        browse_button = customtkinter.CTkButton(browse_frame, text="Browse", command=lambda: self.browsefunc(self.entry_browse), font=("Roboto", 14))
        browse_button.grid(row=0, column=1, padx=20, pady=20, sticky="w")

    def browsefunc(self, entry):
        filename = customtkinter.filedialog.askdirectory()
        if filename:
            entry.configure(textvariable=customtkinter.StringVar(value=filename))


# ---------------------------------------------------------------------------- #
#                                  Main Object                                 #
# ---------------------------------------------------------------------------- #
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Window
        self.title("Berried DL v.1.03 - reclaimer of my yt videos")
        self.iconbitmap(f'{os.path.join(PATH_ROOT, "images")}//icon3.ico')
        self.geometry(f"{1050}x{800}")
        self.minsize(900,340)

        # Grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Picture
        image_path = os.path.join(PATH_ROOT, "images")
        self.img = customtkinter.CTkImage(Image.open(os.path.join(image_path, "label4.png")), size=(250, 300))
        
        self.corp_pic_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.corp_pic_frame.grid(row=0, column=0, sticky="nw", rowspan=2)

        self.corp_pic_frame_label = customtkinter.CTkLabel(self.corp_pic_frame, text="", image=self.img)
        self.corp_pic_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.settings_frame = SettingsFrame(self)
        self.settings_frame.grid(row=0, column=1, padx=25, pady=(25,0), sticky="nwe")

        # Start Button
        self.button = customtkinter.CTkButton(self, text="Start", command=self.button_callback_threaded, height=40, font=("Helvetica", 17, 'bold'), fg_color='#496F4E', hover_color='#38563D')
        self.button.grid(row=1, column=1, padx=10, pady=0, sticky="n") #, columnspan=2

        # Logs
        self.log_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.log_frame.grid(row=2, column=0, sticky="nsew", columnspan=2)
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(self.log_frame, width=5000, height=5000, corner_radius=0, wrap=customtkinter.WORD, font=("Consolas", 14), fg_color="#181818") #, state="disabled"
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)

        # tags
        # API was changed to allow font in tags
        self.textbox.tag_config('info_label', font=("Consolas", 14), foregroun="#159acd")
        self.textbox.tag_config('highlight1', foregroun="#f5f543") # yellow
        self.textbox.tag_config('highlight2', foregroun="#7F7F7F") # grey
        self.textbox.tag_config('highlight3', font=("Consolas", 14), foregroun="#a2d9a1") #green
        self.textbox.tag_config('highlight4', foregroun="#F44747") # red
        self.textbox.tag_config('highlight5', foregroun="#47f49e") # green
        
        self.textbox.insert("0.0", "Download Log:\n", 'info_label')
        
        self.textbox.see("end")

        self.textbox.configure(state='disabled')
        
    def button_callback(self):
        # create folder if didn't exist already
        Path(self.settings_frame.entry_browse.get()).mkdir(parents=True, exist_ok=True)

        # main logic
        media_type = self.settings_frame.settings.radio_state.get()
        if (media_type == RADIO_NAMES[0]):
            media_type = 'video'
        elif (media_type == RADIO_NAMES[1]):
            media_type = 'audio'
        elif (media_type == RADIO_NAMES[2]):
            media_type = 'both'
        url = self.settings_frame.entry_field.get()
        dl_dir = self.settings_frame.entry_browse.get()

        self.gui_disable()

        if url != '':
            try:
                BerriedDL.main(media_type, url, dl_dir, self.textbox, True)
            except Exception as err:
                self.textbox.configure(state='normal')
                self.textbox.insert("end", "\n", 'highlight4')
                self.textbox.insert("end", "\n", 'highlight4')
                self.textbox.insert("end", "Something went wrong! - better restart the app\n", 'highlight4')
                self.textbox.insert("end", "\n", 'highlight4')
                self.textbox.insert("end", "If this issue reproduces, please report it: https://github.com/pain-peko/Berried_DL/issues\n", 'highlight4')
                self.textbox.insert("end", "\n", 'highlight4')
                self.textbox.insert("end", f"{type(err)}\n", 'highlight4')
                self.textbox.insert("end", f"{err.args}\n", 'highlight4')
                self.textbox.insert("end", f"{err}\n", 'highlight4')
                self.textbox.insert("end", "\n", 'highlight4')
                self.textbox.insert("end", "\n", 'highlight4')
                self.textbox.see("end")
                self.textbox.configure(state='disabled')

        self.gui_enable()
        

    def button_callback_threaded(self):
        t1 = threading.Thread(target=self.button_callback)
        t1.start()

    def gui_disable(self):
        self.button.configure(state='disabled')
        for radio in self.settings_frame.radiobuttons:
            radio.configure(state='disabled')

    def gui_enable(self):
        self.button.configure(state='normal')
        for radio in self.settings_frame.radiobuttons:
            radio.configure(state='normal')


# ---------------------------------------------------------------------------- #
#                                      Run                                     #
# ---------------------------------------------------------------------------- #
app = App()

def window_exit():
    # Save settings
    with open(os.path.join(PATH_CONFIG, "settings.json"), "w") as file:
        app.settings_frame.settings.dlpath = app.settings_frame.entry_browse.get()
        app.settings_frame.settings.preJSON()
        json.dump(jsonpickle.encode(app.settings_frame.settings), file)

    # Close app
    app.destroy()
app.protocol("WM_DELETE_WINDOW", window_exit)

app.mainloop()
