
import re


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def textbox_append(textbox, str, tag=False, see=True):
    if textbox == False:
        print(str, end="")
        return
    
    str = escape_ansi(str)

    textbox.configure(state='normal')

    if tag:
        textbox.insert("end", f"{str}", tag)
    else:
        textbox.insert("end", f"{str}")

    if see:
        textbox.see("end")

    textbox.configure(state='disabled')

def textbox_replace_lastline(textbox, str, tag=False):
    if textbox == False:
        print("\033[A\033[A")
        textbox_append(textbox, str, tag)
        return

    textbox.configure(state='normal')
    textbox.delete("end-2l","end-1l")
    textbox.configure(state='disabled')
    textbox_append(textbox, str, tag, False)

class Logbox:
    def __init__(self, file, textbox=False):
        self.file = file
        self.textbox = textbox
        
        self.progress_bar = False

    def debug(self, msg, print_this=False):
        if msg is None:
            return
        
        msg = msg + '\n'
        
        self.file.write(escape_ansi(msg))

        self.print_useful_msg(msg, print_this)

    def warning(self, msg):
        msg = msg + '\n'
        msg = f'WARNING: {msg}'

        self.file.write(escape_ansi(msg))

        if '[youtube:tab] Incomplete data received.' in msg:
            return
        else:
            textbox_append(self.textbox, msg)

    def error(self, msg):
        msg = msg + '\n'
        msg = f'ERROR: {msg}'
        msg = '\n' + msg + '\n'

        self.file.write(escape_ansi(msg))

        textbox_append(self.textbox, msg, 'highlight5')

    def print_useful_msg(self, str, print_this=False):

        # avoid filter
        if print_this:
            textbox_append(self.textbox, str)
            return

        # filter
        if '[info]' in str:
            if 'format(s):' in str:
                textbox_append(self.textbox, str, 'highlight1')
                return
            
            textbox_append(self.textbox, str, 'highlight2')
            return
        
        if '[debug] Command-line config:' in str:
            textbox_append(self.textbox, str)
            return
        
        if '[VideoRemuxer]' in str:
            textbox_append(self.textbox, str)
            return
        
        if '[ThumbnailsConvertor]' in str:
            textbox_append(self.textbox, str)
            return

        if 'Deleting original file' in str:
            textbox_append(self.textbox, str)
            return
        
        if '[download] Destination:' in str:
            textbox_append(self.textbox, str, 'highlight1')
            return
        
        if '[Merger]' in str:
            textbox_append(self.textbox, str, 'highlight1')
            return
        
        if '[ExtractAudio] Destination: ' in str:
            textbox_append(self.textbox, '\n')
            textbox_append(self.textbox, str, 'highlight5')
            return
        
        # playlists
        if '[youtube:tab] Extracting URL: ' in str:
            textbox_append(self.textbox, str)
            return
        
        if '[youtube:tab] Playlist' in str:
            textbox_append(self.textbox, str, 'highlight1')
            return

        if '[download] Downloading item' in str:
            strs = str.split('item')
            strs[0] = '[download] Webpage for item'
            textbox_append(self.textbox, strs[0] + strs[1], 'highlight6')
            return

        if '[youtube] Extracting URL: ' in str:
            textbox_append(self.textbox, str)
            return
        
        if '[download] Prepearing item' in str:
            textbox_append(self.textbox, str, 'highlight6')
            return

        # progress bar
        if ('[download]' in str) and (('%' in str) or ('(frag' in str)):
            if '100%' in str:
                # first progress bar is already 100% protection
                if not self.progress_bar: 
                    textbox_append(self.textbox, '\n')
                    textbox_append(self.textbox, '\n')
                    
                textbox_replace_lastline(self.textbox, str, 'highlight5')
                textbox_append(self.textbox, '\n')
                self.progress_bar = False
                return
            
            if not self.progress_bar:
                self.progress_bar = True
                textbox_append(self.textbox, '\n')
                textbox_append(self.textbox, str, 'highlight4')
                return
            
            textbox_replace_lastline(self.textbox, str, 'highlight4')
            return
        
        # finished
        if 'has already been downloaded' in str:
            textbox_append(self.textbox, '\n')
            textbox_append(self.textbox, str, 'highlight5')
            textbox_append(self.textbox, '\n')
            return

        if 'Download finished, detailed log' in str:
            textbox_append(self.textbox, str, 'highlight3')
            textbox_append(self.textbox, '\n')
            textbox_append(self.textbox, '\n')
            return
