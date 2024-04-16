from logbox import escape_ansi
from logbox import textbox_append

class Info_Logbox:
    def __init__(self, file, textbox=False):
        self.file = file
        self.textbox = textbox

    def debug(self, msg):
        if msg is None:
            return
        
        msg = msg + '\n'
        self.file.write(escape_ansi(msg))
        # logbox: nothing

    def warning(self, msg):
        msg = msg + '\n'
        msg = f'WARNING: {msg}'

        self.file.write(escape_ansi(msg))
        textbox_append(self.textbox, msg)

    def error(self, msg):
        msg = msg + '\n'
        msg = f'ERROR: {msg}'
        msg = '\n' + msg + '\n'

        self.file.write(escape_ansi(msg))
        textbox_append(self.textbox, msg, 'highlight5')