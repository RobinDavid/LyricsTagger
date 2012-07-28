LyricsTagger
============

Python program, that automaticaly tag lyrics in MP3 files.
Article with screenshots: http://robindavid.comli.com/lyricstagger/

Why write LyricsTagger
----------------------

I have written LyricsTagger due to the lack of software to tag lyrics in MP3's. Moreover of what I know there is no any free and open source lyrics database available.
From my point of view lyricsmania is the best website for lyrics with the best amount of lyrics, but the database is not available.
So LyricsTagger act like a crawler to find lyrics fetch the webpage which is containing lyrics exctract them and put them in the right MP3.

How to use it ?

LyricsTagger is written in python using PyQt and mutagen (for mp3 tag manipulation).
Once you have launched it, just provide the directory or the file to tag. The program will then read the the artist and the title 
of the each song in theirs tags and will try to find the lyrics on lyricsmania/parolesmania.
Note: The pogram do quite a lot of request the site so don't try to tag your hole library or you will be banned from lyricsmania (for almost 2 weeks).
Note: The program sometimes bugs for an unknown reason and stay locked on a song. So if it happens kill the program and relaunch it.