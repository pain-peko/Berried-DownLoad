
class Logbox:
    flag = False
    progress_bar = False

    def print(str):
        print(str, end="")

    def dump(textbox, str):
        # next strings are printed
        if '[info] Available formats' in str:
            Logbox.flag = True
            return

        # print this
        if '[info]' in str:
            if 'format(s):' in str:
                Logbox.textbox_append(textbox, str, 'highlight1')
                return
            
            Logbox.textbox_append(textbox, str, 'highlight2')
            return
        
        if '[debug] Command-line config:' in str:
            Logbox.textbox_append(textbox, str)
            return
        
        if '[VideoRemuxer]' in str:
            Logbox.textbox_append(textbox, str)
            return
        if 'Deleting original file' in str:
            Logbox.textbox_append(textbox, str)
            return
        
        if '[download] Destination:' in str:
            Logbox.textbox_append(textbox, str, 'highlight1')
            return
        
        if '[Merger]' in str:
            Logbox.textbox_append(textbox, str, 'highlight1')
            return
        
        if '[ExtractAudio] Destination: ' in str:
            Logbox.textbox_append(textbox, str, 'highlight5')
            return

        if ('[download]' in str) and (('%' in str) or ('(frag' in str)):
            if '100%' in str:
                # first progress bar is already 100% protection
                if not Logbox.progress_bar: 
                    Logbox.textbox_append(textbox, '\n')
                    Logbox.textbox_append(textbox, '\n')
                    
                Logbox.textbox_replace_lastline(textbox, str, 'highlight5')
                Logbox.textbox_append(textbox, '\n')
                Logbox.progress_bar = False
                return
            
            if not Logbox.progress_bar:
                Logbox.progress_bar = True
                Logbox.textbox_append(textbox, '\n')
                Logbox.textbox_append(textbox, str, 'highlight4')
                return
            
            Logbox.textbox_replace_lastline(textbox, str, 'highlight4')
            return
        
        if 'has already been downloaded' in str:
            Logbox.textbox_append(textbox, '\n')
            Logbox.textbox_append(textbox, str, 'highlight5')
            Logbox.textbox_append(textbox, '\n')
            return
        
        if 'newline' == str:
            Logbox.textbox_append(textbox, '\n')
            return

        if 'Download finished, detailed log' in str:
            Logbox.textbox_append(textbox, str, 'highlight3')
            Logbox.textbox_append(textbox, '\n')
            Logbox.textbox_append(textbox, '\n')
            return

        # stop printing condition
        if Logbox.flag:
            if 'info_over' == str:
                Logbox.flag = False
            else:
                Logbox.textbox_append(textbox, str)
            return

        #Logbox.textbox_append(textbox, str)

    def textbox_append(textbox, str, tag=False, see=True):
        if textbox == False:
            Logbox.print(str)
            return
        
        textbox.configure(state='normal')

        if tag:
            textbox.insert("end", f"{str}", tag)
        else:
            textbox.insert("end", f"{str}")

        if see:
            textbox.see("end")

        textbox.configure(state='disabled')

    def textbox_replace_lastline(textbox, str, tag=False):
        textbox.configure(state='normal')
        textbox.delete("end-2l","end-1l")
        textbox.configure(state='disabled')
        Logbox.textbox_append(textbox, str, tag, False)
