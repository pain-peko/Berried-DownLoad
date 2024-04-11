import os
import yt_dlp

PATH_ROOT = os.path.dirname(os.path.realpath(__file__))
PATH_DL = os.path.join(PATH_ROOT, "downloads")

def gen_opts(dl_dir):
    ydl_opts = {
        'verbose': True,                                                    # full debug
        'ignoreerrors': 'only_download',                                    # Do not stop on postprocessing errors
        'outtmpl': {'default': f'{dl_dir}\%(title)s\%(title)s.%(ext)s'},    # Output path

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

def gen_audio_opts(dl_dir):
    ydl_opts = gen_opts(dl_dir)

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

def gen_video_opts(dl_dir):
    ydl_opts = gen_opts(dl_dir)

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


def main(media_type):
    dl_dir = PATH_DL
    URL = 'https://youtu.be/d3UTywBDSW4?si=s-hgg1mRqQJO4tVg'

    # print available formats
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(URL, download=False)
        ydl.list_formats(info)

    # download audio
    if media_type != 'video':
        ydl_opts = gen_audio_opts(dl_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(URL)
    
    # download video and metadata
    if media_type != 'audio':
        ydl_opts = gen_video_opts(dl_dir)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(URL)
        

if __name__ == "__main__":
    main(3)
    