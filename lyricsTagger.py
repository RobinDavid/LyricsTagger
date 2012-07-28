#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ParolesManiaGrabber import ParolesManiaGrabber # my Grabing module

# Mutagen packages
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, USLT
from compatid3 import CompatID3
#--------------
from optparse import OptionParser

import os, sys, re

OVERRIDE_EXISTING_LYRICS=True       #Override existing lyrics in mp3 file if set to True
RECURSIVE=True                     #Do a recursive search for mp3 files on the given path
COMPATIBILITY_WMP=True              #Will save tags in ID3 v2.3 instead of 2.4(the newest) because Windows Media Player doesn't support it 

hand = ParolesManiaGrabber()
artist = ""
title = ""
artist_skipped = False #used if artist skipped once, will skip all the following songs with the same artist
file_handler=None

def log(to_log,nb_tab=0):
    print("\t"*nb_tab+to_log)
    file_handler.write("\t"*nb_tab+to_log+"\n")

def processFile(filename): #Main function.
    log(filename)
    name = os.path.split(filename)[1]
    # create ID3 tag if not exists
    try: 
        tags = ID3(filename)
        newtags = MP3(filename)
    except ID3NoHeaderError:
        log("Adding ID3 header",1)
        tags = ID3()
    
    global artist #Write it because it's forbidden in python to assign a variable without having declared it before in a block
    global artist_skipped
    # Change artist only if the new read one is different to avoid useless artist_link requests
    if tags.get("TPE1") is not None:
        newartist = tags.get("TPE1")[0]
        if newartist != artist: #set new artist only if he is new
            if hand.setArtist(newartist) is None:#Update only when artist change
                
                ''' Easy way to do
                if hand.chooseArtist():
                    print "Artist choosen !"
                else:
                    print "Artist skipped !"
                '''    
                #------------------------------------------
                mylist = hand.getAvailableArtists()
                print "0. Skip this Artist"
                for i in range(len(mylist)):
                    print i+1,". ",mylist[i][0]
                    i = i + 1
                c = raw_input("You choice: ")
                c = int(c)       
                if c == 0:
                    log("Artist skipped (choosed by user)!",1)
                    artist_skipped=True
                    return False
                else:
                    try:
                        hand.resumeSetArtist(c-1)
                    except IndexError:
                        log("Bad choice (artist Skipped)",1)
                        return False  
                #--------------------------------------------      
                    
            else:
                artist_skipped=False
                artist = newartist
                log("Artist New: "+artist,1)

        else:
            log("Artist Same: "+artist,1)
            if artist_skipped:
                return False
    else:
        log("Artist name not found in ID3 Tags (TPE1)",1)
        log(name+" skipped",1)
        return False
    
    
    global title    
    if tags.get("TIT2")[0] != title: #Will probably get into each processFile call    
        title = tags.get("TIT2")[0]
        if title is not None:
            res = hand.setTitle(title)
            if res is None:
                ''' Easy way to do
                if hand.chooseTitle():
                    print "Title choosen !"
                else:
                    print "Title skipped !"
                    return False
                '''    
                #------------------------------------------
                mylist = hand.getAvailableTitles()
                print "0. Skip this Song"
                for i in range(len(mylist)):
                    print i+1,". ",mylist[i][0]
                    i = i + 1
                c = raw_input("You choice: ")
                c = int(c)       
                if c == 0:
                    log ("Song skipped (choosed by user)!",1)
                    return False
                else:
                    try:
                        hand.resumeSetTitle(c)
                        if hand.lyricsFound():
                            log("Lyrics found !",1)
                        else:
                            log("No lyrics for this song !",1)
                    except IndexError:
                        log("Bad choice (Song Skipped)",1)
                        return False  
                #--------------------------------------------                  
                
            elif not res:
                log("Artist not set",1)
                return False
            else:
                if hand.lyricsFound():
                    log("Lyrics found !",1)
                else:
                    log("No lyrics for this song !",1)
        else:
            log("Title field not found in ID3 Tags (TIT2)",1)
            log(name+" skipped",1)
            return False
    
    #-----------------------------------------------------
            
    #!! At this point artist and title are correctly set !    
    #print "Artist: ", artist,"\tTitle: ",title
    ly_exist = False
    ly_header = ""
    
    #Lookup in mp3 tags if it contains lyrics
    for head in tags.keys(): # For all keys
        if re.search("USLT::",head): #if keys contain USLT
            if len(tags.getall(head)) != 0: #    
                ly_exist = True
                ly_header = head   
    
    
    if not hand.lyricsFound(): #Lyrics are NOT found
        if ly_exist:
            log("Lyrics already tagged (skipped)",1)
            return True #We keep existing lyrics
        else:
            log("Lyrics not found in tags ",1)
            return False #No existing lyrics and not found on website
    else: #Lyrics are found on parolesmania
        if ly_exist:
            if OVERRIDE_EXISTING_LYRICS: #If lyrics already exist and override true we should  delete them before
                # remove old unsychronized lyrics
                log("Remove old Lyrics in tags",1)
                if not COMPATIBILITY_WMP: #because if enable useless to remove USLT
                    tags.delall(ly_header)
                    tags.save(filename)
            else: #Lyrics already exist and we should not override them so just exit true
                log("Lyrics already exist skip",1)
                return True

        #From here lyrics will be written in the file anyway    
        lyrics = hand.getLyrics()
            
        # USLT frames are present
        if not COMPATIBILITY_WMP:
            tags[u"USLT::'eng'"] = (USLT(encoding=1, lang=u'fre', desc=u'', text=lyrics))
            tags.save(filename)    
        else:#Alternative for windows because not compatible with 2.4
            newtags.delete()
            #newtags.save(filename)
            newtags = MP3(filename)
            newtags.add_tags(ID3=CompatID3)
            
            for e in tags.keys(): #Recopy old frames but not old lyrics!
                if not (ly_exist and e == ly_header):
                    newtags[e] = tags.get(e)
                else:
                    pass
                    #print e, " Skipped old lyrics!"
            
            #Itunes seems to like encoding=1 'eng' and
            #WIndows Media Player prefer 'fre'         
            newtags[u"USLT::'eng'"] = (USLT(encoding=1, lang=u'fre', desc=u'', text=lyrics))
                
            newtags.tags.update_to_v23()
        
            #Finally save tags to the file
            newtags.tags.save(filename,v2=3)
        log('Lyrics Added to '+name,1)    
        return True

def dirLookup(dir_path):
    if os.path.isfile(dir_path):#TODO: Add print everywhere for backtrack !
        if processFile(dir_path): #log if returned value is false etc..
            log("OK\n")
        else:
            log("Failed\n")
            
    elif os.path.isdir(dir_path):        
        for fn in os.listdir(dir_path):
            currentfile = os.path.join(dir_path, fn)
            if RECURSIVE and os.path.isdir(currentfile):
                dirLookup(currentfile) #Make a recursive call if is a directory
            elif currentfile.lower().endswith('.mp3'):
                dirLookup(currentfile) # Make also a recursive call 

if __name__ == "__main__":
    usage="usage: tagger.py [options] filename/dirname f2 .."
    parser = OptionParser(usage=usage, version="1.0")
    parser.add_option("-o","--nooverride", default=True, action="store_false",dest="override" ,help="Override existing lyrics in mp3 files") # cannot use action="store_false",dest="OVERRIDE_EXISTING_LYRICS"
    parser.add_option("-r","--norecursive", default=True, action="store_false", dest="recur", help="Look recursively into folders to find mp3 files")
    parser.add_option("-c","--nocompatibility", default=True,action="store_false",dest="compat" ,help="Enable compatibility mode for Windows Media Player (save Tags in ID3 v2.3 instead of the newest 2.4)")
    parser.add_option("-v", action="store_true", dest="verbose", help="Activate verbosity for technical informations (default)")
    parser.add_option("-q", action="store_false", dest="verbose", help="Do not show technical informations",default=False)
    
    options, args = parser.parse_args()
    
    file_handler = open("tagger.log", "w")
    
    if options.override:
        log("Override existing lyrics: YES")
    else:
        OVERRIDE_EXISTING_LYRICS=False
        log("Override existing lyrics: NO")
    if options.recur:
        log("Recursive search: YES")
    else:
        RECURSIVE = False
        log("Recursive search: NO")
    if options.compat:
        log("Compatibility mode for Windows Media Player: YES\n")
    else:
        COMPATIBILITY_WMP=False
        log("Compatibility mode for Windows Media Player: NO\n")
        
    hand.setVerbosity(options.verbose)
    
    if len(args) < 1:
        parser.error("The filename or directory name is needed")
    else:
        for path_to_process in args:
            try:
                path = os.path.abspath(path_to_process)
                dirLookup(path)
            except KeyboardInterrupt:
                print "Interrupted by user"
                sys.exit(1)    
      
    log("\nDone")

    file_handler.close()
    
    sys.exit(0)