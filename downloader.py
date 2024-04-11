## TODO:
# 7. make cool executable, that makes windows shortcut and stuff
# 9. make all pathes relative!!!
# 10. Change yt-dlp path added when installing the program
# 11. Create metadata editor as separate file in the end of a program
#     Use data from created json
# 12. Rename Subtitles to have Japanese\English and not just number

## comments
#'--embed-subs',
#'--convert-subs',
#'ass',
#'en.*,ja.*',
#'--sub-format',
#'ass/srt/best',
#'--write-comments'

import os
import subprocess
import sys
from termcolor import colored
from datetime import datetime
from pathlib import Path
from logbox import Logbox
import cli_to_api

from pprint import pprint



# ---------------------------------------------------------------------------- #
#                                    Consts                                    #
# ---------------------------------------------------------------------------- #
DETAILED_DEBUG = True
PATH_ROOT = os.path.dirname(os.path.realpath(__file__))
PATH_DL = os.path.join(PATH_ROOT, "downloads")
YT_DLP_PATH = "D:\DSoftware\yt-dlp\yt-dlp.exe" 



# ---------------------------------------------------------------------------- #
#                                    Command                                   #
# ---------------------------------------------------------------------------- #

def audio_cmd(cmd):
    # Formatting
    cmd.extend(['-f', 'bestaudio', '-x'])

def video_cmd(cmd):
    # Formatting
    cmd.extend(['-f', 'bestvideo*+bestaudio/best'])

    # Subs
    cmd.append('--write-sub')
    cmd.append('--sub-langs')
    cmd.append('all')

    # remux to matroska (if video)]
    cmd.append('--remux-video')
    cmd.append('mkv')

    # chapters
    cmd.append('--embed-chapters')

def create_cmd(media_type, repeated_flag, url, dl_dir):

    if (media_type != 'video' and media_type != 'audio'):
        print(colored('func create_cmd, media_type must be "video" or "audio"', 'red'))
        sys.exit()

    # Base
    cmd = [YT_DLP_PATH, '-o', f'{dl_dir}\%(title)s\%(title)s.%(ext)s']

    # Debugging
    if DETAILED_DEBUG:
        cmd.append('--verbose')

    # Media type specific
    if (media_type == 'video'):
        video_cmd(cmd)
    else:
        audio_cmd(cmd)

    if repeated_flag == False:
        # Pull info
        cmd.extend(['--write-thumbnail',
                    '--write-description',
                    '--write-info-json',
                    '--write-annotations',
                    '--write-url-link'])

    # post-processing
    cmd.extend(['--convert-thumbnails', 'png'])
    cmd.append('--embed-thumbnail')
    cmd.append('--embed-metadata')

    # URL
    cmd.append(url)

    return cmd

def show_list_cmd(url):
    cmd = [YT_DLP_PATH, '--list-formats', url]
    if DETAILED_DEBUG:
        cmd.append('--verbose')
    
    return cmd



# ---------------------------------------------------------------------------- #
#                                    Execute                                   #
# ---------------------------------------------------------------------------- #
def execute(cmd, si):
    print('\nThe arguments passed translate to:\n')
    pprint(cli_to_api.cli_to_api(cmd))
    print('\nCombining these with the CLI defaults gives:\n')
    pprint(cli_to_api.cli_to_api(cmd, True))

    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, startupinfo=si)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)



# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #
def main(media_type, url, dl_dir, textbox=False):

    # hide yt-dlp windows
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # Open log file
    now = datetime.now()
    now = now.replace(microsecond=0)
    now = str(now).replace(':', '-')
    now = now.split(' ')
    if os.path.basename(PATH_ROOT) == 'Data':
        log_dir_path = f'{os.path.dirname(PATH_ROOT)}\\logs'
    else:
        log_dir_path = f'{PATH_ROOT}\\logs'
    Path(log_dir_path).mkdir(parents=True, exist_ok=True)
    log_file = f'{log_dir_path}\\[{now[0]}] [{now[1]}] example_name.log'
    f = open(log_file, "w")

    # Available formats
    f.write('\n\n\n\n\n')
    for path in execute(show_list_cmd(url), si):
        f.write(path)
        Logbox.dump(textbox, path)
    Logbox.dump(textbox, 'info_over')
    Logbox.dump(textbox, 'newline')

    # Download chosen format
    Logbox.dump(textbox, 'dl_start')
    f.write('\n\n\n')
    if (media_type != 'both'):
        for path in execute(create_cmd(media_type, False, url, dl_dir), si):
            f.write(path)
            Logbox.dump(textbox, path)
    else:
        for path in execute(create_cmd('audio', True, url, dl_dir), si):
            f.write(path)
            Logbox.dump(textbox, path)
        Logbox.dump(textbox, 'newline')
        for path in execute(create_cmd('video', False, url, dl_dir), si):
            f.write(path)
            Logbox.dump(textbox, path)   
    Logbox.dump(textbox, 'newline')
    # Close log
    f.close()

    # Rename log
    name_found = False
    for _ in (True,):
        with open(log_file, 'r') as filedata:
            for line in filedata:
                if (f"to: {dl_dir}" in line):
                    result = line.split(dl_dir)
                    title = result[1].split('\\')
                    title = title[1]
                    name_found = True
                    break

    new_log_file = log_file
    if name_found:
        new_log_file = f'{log_dir_path}\\[{now[0]}] [{now[1]}] {title}.log'
        os.rename(log_file, new_log_file)

    Logbox.dump(textbox, f'Download finished, detailed log saved to: {new_log_file}')


if __name__ == "__main__":
    # Handle arg URL 
    ERROR = 0
    if len(sys.argv) != 3:
        ERROR = 1
        
    if (sys.argv[1] != 'video' and sys.argv[1] != 'audio' and sys.argv[1] != 'both'):
        ERROR = 1

    if ERROR == 1:
        print(colored("Function is called wrong", 'red'))
        print(colored('You must use the form: python main.py media_type https://www.example_url.com\nmedia_type can be "audio", "video" or "both" (without quotes)', 'red'))
        sys.exit()

    if sys.argv[1] == 'video':
        MEDIA_TYPE = 'video'
    elif sys.argv[1] == 'audio':
        MEDIA_TYPE = 'audio'
    elif sys.argv[1] == 'both':
        MEDIA_TYPE = 'both'

    URL = sys.argv[2]

    Path(PATH_DL).mkdir(parents=True, exist_ok=True) # create folder if didn't exist already
    main(MEDIA_TYPE, URL, PATH_DL)

