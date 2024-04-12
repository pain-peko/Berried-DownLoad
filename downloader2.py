from datetime import datetime
import os
import yt_dlp
from logbox2 import Logbox
from pathlib import Path

# ---------------------------------------------------------------------------- #
#                                    Consts                                    #
# ---------------------------------------------------------------------------- #
PATH_ROOT = os.path.dirname(os.path.realpath(__file__))
PATH_DL = os.path.join(PATH_ROOT, "downloads")
filename = ''


# ---------------------------------------------------------------------------- #
#                                Progress hooks                                #
# ---------------------------------------------------------------------------- #
def my_hook(d):
    if d['status'] == 'started':
        filename = d['filename']
        print(filename)


# ---------------------------------------------------------------------------- #
#                                   dl params                                  #
# ---------------------------------------------------------------------------- #
def gen_info_opts(logfile, textbox):
    ydl_opts = {
        'logger': Logbox(logfile, textbox)
    }

    return ydl_opts

def gen_opts(dl_dir, logfile, textbox):
    ydl_opts = {
        'verbose': True,                                                    # full debug
        'ignoreerrors': 'only_download',                                    # Do not stop on postprocessing errors
        'outtmpl': {'default': f'{dl_dir}\%(title)s\%(title)s.%(ext)s'},    # Output path

        'progress_hooks': [my_hook],
        'logger': Logbox(logfile, textbox),

        'writethumbnail': True,

        'postprocessors': [{
                'key': 'FFmpegThumbnailsConvertor',     # Convert thumbnail to PNG
                'format': 'png',
                'when': 'post_process'
            },{
                'key': 'FFmpegMetadata',                # Insert Metadata
                'add_chapters': True,
                'add_infojson': 'if_exists',
                'add_metadata': True
            }]
    }
    
    return ydl_opts

def gen_audio_opts(dl_dir, logfile, textbox):
    ydl_opts = gen_opts(dl_dir, logfile, textbox)

    ydl_opts['format'] = 'bestaudio'

    ydl_opts['postprocessors'].append({
        'key': 'FFmpegExtractAudio',        # Extract audio                                   
        'nopostoverwrites': False,
        'preferredcodec': 'best',
        'preferredquality': '0'
    })

    ydl_opts['postprocessors'].append({
        'key': 'EmbedThumbnail',            # Insert Thumbnail and without keeping it as a separate file
        'already_have_thumbnail': False
    })
    
    return ydl_opts

def gen_video_opts(dl_dir, logfile, textbox):
    ydl_opts = gen_opts(dl_dir, logfile, textbox)

    ydl_opts['format'] = 'bestvideo*+bestaudio/best'

    ydl_opts['final_ext'] = 'mkv'

    # Download all non-automatic subs, description, metadata etc
    ydl_opts['subtitleslangs'] = ['all']
    ydl_opts['writethumbnail'] = True
    ydl_opts['writeannotations'] = True
    ydl_opts['writedescription'] = True
    ydl_opts['writeinfojson'] = True
    ydl_opts['writesubtitles'] = True
    ydl_opts['writeurllink'] = True

    ydl_opts['postprocessors'].append({
        'key': 'FFmpegVideoRemuxer',        # Put into matroska container
        'preferedformat': 'mkv'
    })

    ydl_opts['postprocessors'].append({
        'key': 'EmbedThumbnail',            # Insert thumbnail and keep it as separate as well
        'already_have_thumbnail': True
    })
    
    return ydl_opts

# ---------------------------------------------------------------------------- #
#                                     main                                     #
# ---------------------------------------------------------------------------- #

def main(media_type, url, dl_dir, textbox=False):

    # open log file
    now = datetime.now()
    now = now.replace(microsecond=0)
    now = str(now).replace(':', '-')
    now = now.split(' ')
    if os.path.basename(PATH_ROOT) == 'Data':
        log_dir_path = f'{os.path.dirname(PATH_ROOT)}\\logs'
    else:
        log_dir_path = f'{PATH_ROOT}\\logs'
    Path(log_dir_path).mkdir(parents=True, exist_ok=True)
    logfile = f'{log_dir_path}\\[{now[0]}] [{now[1]}] example_name.log'
    file = open(logfile, "w")

    # print available formats
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        info = ydl.render_formats_table(info)

        lbox = Logbox(file, textbox)
        lbox.debug(info, True)
        lbox.debug('', True)

    # download audio
    if media_type != 'video':
        ydl_opts = gen_audio_opts(dl_dir, file, textbox)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
        Logbox(file, textbox).debug('', True)
    
    # download video and metadata
    if media_type != 'audio':
        ydl_opts = gen_video_opts(dl_dir, file, textbox)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
        Logbox(file, textbox).debug('', True)

    new_log_file = 'hello world'
    Logbox(file, textbox).debug(f'Download finished, detailed log saved to: {new_log_file}')
    file.close()
        

if __name__ == "__main__":
    dl_dir = PATH_DL
    url = 'https://youtu.be/xyx8DMlUAQ4?si=vKoLdn5fW0gsffpc'
    #url = 'https://youtu.be/d3UTywBDSW4?si=s-hgg1mRqQJO4tVg'
    main('both', url, dl_dir)
    