import mutagen

def main(name):

    audio = mutagen.File(name)
    print(audio.pprint())

    # date
    date = audio["DATE"]
    date = date[0]
    if '-' not in date:
        date = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    audio["DATE"] = date
    
    # album and album artist
    audio["ALBUM"] = audio["TITLE"]
    audio["ALBUMARTIST"] = audio["ARTIST"]

    # track number
    audio["TRACK"] = u'01'

    # URL
    audio["ORIGIN WEBSITE"] = audio["PURL"]
    audio.pop('PURL')

    # Description
    audio["DESCRIPTION"] = audio["SYNOPSIS"]
    audio.pop('SYNOPSIS')

    # misc
    audio["QUALITY"] = u'Medium'
    audio["WWWAUDIOFILE"] = u'YouTube'

    audio["RELEASETYPE"] = u'Single' # Manually change to Playlist \ Album \ EP if you care

    # Picture
    # get it, resize to square and be happy

    # think about the title, how to get it


    print("\n\n\n")
    print(audio.pprint())

    audio.save()

if __name__ == "__main__":
    main("downloads\オーバーライド - 重音テトSV[吉田夜世]\オーバーライド - 重音テトSV[吉田夜世].opus")
    #main('downloads\Mili - In Hell We Live\Mili - In Hell We Live.opus')
