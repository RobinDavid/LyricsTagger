LyricsTagger
============

Python program, that automaticaly tag lyrics in MP3 files.

Why writing LyricsTagger
----------------------

I have written LyricsTagger due to the lack of software to tag lyrics in MP3's. 
From my point of view lyricsmania is the best website for lyrics with the best amount of lyrics, but the database is not available.
So LyricsTagger act like a crawler to find lyrics fetch the webpage which is containing lyrics exctract them and put them in the right MP3.

How to use it ?
---------------

LyricsTagger is written in python using PyQt and mutagen (for mp3 tag manipulation).
Once you have launched it, just provide the directory or the file to tag. The program will then read the the artist and the title 
of the each song in theirs tags and will try to find the lyrics on lyricsmania/parolesmania.
Note: The pogram do quite a lot of request the site so don't try to tag your hole library or you will be banned from lyricsmania (for almost 2 weeks).
Note: The program sometimes bugs for an unknown reason and stay locked on a song. So if it happens kill the program and relaunch it.

How it works ?
--------------

It works like a crawler for parolesmania.com. For a given mp3 LyricsTagger take the artist name and the song title into mp3 tags. Then it does a request for the artist on parolesmania. If the artist is found it parse the HTML page to find the title. If it is also found just follow the link of the song page and parse the result to find lyrics. If lyrics are found they are put into the mp3 file.

Some notes about the software:

* It is able to simply make lyrics lookup for an artist. This is pretty much the same than go on the website and make a research but in more user friendly ;)
* You can tag a single file or a whole filetree
* By default ID3 tags are saved using ID3 v 3.2.3 instead of the newest 3.2.4 because Windows Media Player does not support it yet, and tags would not be recognized anymore in WMP (even though they are there).
* You can choose to override existing lyrics if they exists in the file.
* Each time you launch a tag, a report.txt is created which is a copy of what is showed in the listview.
* Be careful to do not do too much tag in once because (no more than a ~1000) your IP can be banned of the website, and making by the way LyricsTagger useless. ( I know what I'm saying...).

Screenshots
===========

![Main interface](https://raw.github.com/RobinDavid/LyricsTagger/master/screenshot/lyricstagger1.jpg)

![Lyrics view](https://raw.github.com/RobinDavid/LyricsTagger/master/screenshot/lyricstagger2.jpg)
