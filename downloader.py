## TODO:
# 7. make cool executable, that makes windows shortcut and stuff
# 12. Rename Subtitles to have Japanese\English and not just number
# 13. Ignore live chat (make const)
# 14. Playlist support - folder in downloads + the right name for logfile as playlist name + correct display of logs while playlist downloading
# 15. get rid of all prints
# 16. delete description metadata
# 17. delete language


import os
import yt_dlp
from pathlib import Path
from datetime import datetime
from logbox import Logbox
from info_logbox import Info_Logbox
import metadata


# ---------------------------------------------------------------------------- #
#                                    Consts                                    #
# ---------------------------------------------------------------------------- #
PATH_ROOT = os.path.dirname(os.path.realpath(__file__))
PATH_DL = os.path.join(PATH_ROOT, "downloads")
g_targetdir = ''
g_targettitle = ''
g_targetaudio_codec = ''


# ---------------------------------------------------------------------------- #
#                                Progress hooks                                #
# ---------------------------------------------------------------------------- #
def progress_hook(d):
    if d['status'] == 'finished':
        filepath = d['filename']
        title = os.path.basename(filepath)

        global g_targetdir, g_targettitle, g_targetaudio_codec
        g_targetdir = os.path.dirname(filepath)
        g_targettitle = title.split('.')[0]

def postprocess_hook(d):
    if d['status'] == 'finished':
        if d['postprocessor'] == 'ExtractAudio':
            global g_targetaudio_codec
            g_targetaudio_codec = d['info_dict']['acodec']


# ---------------------------------------------------------------------------- #
#                                   dl params                                  #
# ---------------------------------------------------------------------------- #
def gen_logger_opts(logfile, textbox):
    ydl_opts = {
        'logger': Logbox(logfile, textbox)
    }

    return ydl_opts

def gen_logger_opts2(logfile, textbox):
    ydl_opts = {
        'logger': Info_Logbox(logfile, textbox)
    }

    return ydl_opts


def gen_opts(dl_dir, logfile, textbox, playlist_name):
    ydl_opts = {
        'verbose': True,                                                    # full debug
        'ignoreerrors': 'only_download',                                    # Do not stop on postprocessing errors

        'progress_hooks': [progress_hook],
        'postprocessor_hooks': [postprocess_hook],
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

    # Output path
    if playlist_name == None:
        ydl_opts['outtmpl'] = {'default': f'{dl_dir}\\%(title)s\\%(title)s.%(ext)s'}
    else:
        ydl_opts['outtmpl'] = {'default': f'{dl_dir}\\Playlist - {playlist_name}\\%(title)s\\%(title)s.%(ext)s'}

    return ydl_opts

def gen_audio_opts(dl_dir, logfile, textbox, playlist_name):
    ydl_opts = gen_opts(dl_dir, logfile, textbox, playlist_name)

    ydl_opts['format'] = 'bestaudio'

    ydl_opts['postprocessors'].append({
        'key': 'FFmpegExtractAudio',        # Extract audio                                   
        'nopostoverwrites': False,
        'preferredcodec': 'best',
        'preferredquality': '0'
    })

    ydl_opts['postprocessors'].append({
        'key': 'EmbedThumbnail',            # Insert thumbnail and keep it as separate as well
        'already_have_thumbnail': True
    })
    
    return ydl_opts

def gen_video_opts(dl_dir, logfile, textbox, playlist_name):
    ydl_opts = gen_opts(dl_dir, logfile, textbox, playlist_name)

    ydl_opts['format'] = 'bestvideo*+bestaudio/best'

    ydl_opts['final_ext'] = 'mkv'

    # Download all non-automatic subs, description, metadata etc
    ydl_opts['subtitleslangs'] = ['all', '-live_chat']
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

def main(media_type, playlist_url, dl_dir, textbox=False, edit_metadata=False):

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
    file = open(logfile, "w", encoding='utf-8')


    # Detect playlist
    playlist_name = None
    ydl_opts = gen_logger_opts(file, textbox)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if info['extractor'] == 'youtube:tab':
            playlist_name = info['title']

            urls = []
            for entry in info['entries']:
                urls.append(entry['webpage_url'])
            Logbox(file, textbox).debug('', True)
        else:
            urls = [playlist_url]
    
    for url_index, url in enumerate(urls):
        # add new lines for playlists
        if playlist_name != None:
            Logbox(file, textbox).debug('', True)
            Logbox(file, textbox).debug('', True)
            Logbox(file, textbox).debug(f'[download] Prepearing item {url_index + 1} of {len(urls)}')

        # print available formats
        ydl_opts = gen_logger_opts2(file, textbox)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            info = ydl.render_formats_table(info)

            lbox = Logbox(file, textbox)
            lbox.debug(info, True)
            lbox.debug('', True)

        # download audio
        if media_type != 'video':
            ydl_opts = gen_audio_opts(dl_dir, file, textbox, playlist_name)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
            Logbox(file, textbox).debug('', True)

            if edit_metadata:
                metadata.main(f'{g_targetdir}/{g_targettitle}.{g_targetaudio_codec}')
        
        # download video and metadata
        if media_type != 'audio':
            ydl_opts = gen_video_opts(dl_dir, file, textbox, playlist_name)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
            Logbox(file, textbox).debug('', True)


    # close log
    file.close()

    # rename log
    if playlist_name == None:
        new_logfile = f'{log_dir_path}\\[{now[0]}] [{now[1]}] {g_targettitle}.log'
    else:
        new_logfile = f'{log_dir_path}\\[{now[0]}] [{now[1]}] Playlist - {playlist_name}.log'
    os.rename(logfile, new_logfile)

    # success
    file = open(new_logfile, "a", encoding='utf-8')
    Logbox(file, textbox).debug(f'Download finished, detailed log saved to: {new_logfile}')
    file.close()
        

if __name__ == "__main__":
    dl_dir = PATH_DL

    # playlist test
    url = 'https://www.youtube.com/playlist?list=PLADb_O1pgfZsZn_vjEpKV5DFRxNABA0k5'
    main('both', url, dl_dir, False, True)

    # single video test
    url = 'https://youtu.be/xyx8DMlUAQ4?si=vKoLdn5fW0gsffpc'
    main('both', url, dl_dir, False, True)

    url = 'https://youtu.be/3BrtCYZyOXE?si=P8vfDmX9NYEcJAbJ'
    main('audio', url, dl_dir, False, True)

    url = 'https://youtu.be/9kQ2GtvDV3s?si=zqScgDDiBvFpkgjC'
    main('video', url, dl_dir, False, True)
    
