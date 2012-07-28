from HTMLParser import HTMLParser
import httplib, urllib, re
from urlparse import urlparse
import os

#os.environ["http_proxy"] = "http://174.139.255.195:80"

class ParolesManiaGrabber():
    
    #Global vars used averywhere along the code
    WEBSITE = "www.parolesmania.com"
    
    research = "recherche.php" #searchnew.php
    paroles = " paroles" # lyrics
    parolesde ="Paroles De " # lyrics
    
    lyrics = ""
    artist=None
    title=None
    verbose=False
    log_stack=""
    artist_selection= list()
    artist_select_hand=None
    title_selection=list()
    title_hand=None
    proxy = {}
    
    def __init__(self, artist=None, title=None, verbose=False):
        if artist is not None: self.setArtist(artist)
        if title is not None: self.setTitle(title)
        self.artist_page=None
        self.verbose=verbose
    
    def getLyrics(self):
    #Return lyrics 
        return self.lyrics
        
    def lyricsFound(self):
        return self.lyrics != ""
    
    def setProxy(self,pro):
        if pro == "":
            self.proxy = {}
        else:
            self.proxy = {"http":pro}
    
    def setVerbosity(self,value):
        self.verbose = value
        print "Put verbosity to: ", value
    
    def log(self,to_log):
        self.log_stack+=to_log+"\n"
        if self.verbose:
            print to_log
    
    def flush_log(self):
        tmp = self.log_stack
        self.log_stack = ""
        return tmp
        
    '''----------------------------------
    -------- Artist lookup stuff --------
    ----------------------------------'''
    def setArtist(self, artist):
    # Once an artist is recieved update of artist link and page is triggered (so artist selection also ..)
        self.lyrics =""
        self.artist = artist
        artist_link = self.getArtistLink(self.artist) # gather artist URL in order to get the content
        if artist_link is not None:
            self.artist_page = self.getArtistPage(artist_link) # download HTML code to parse it afterwards
            return True
        else:
            return None
    
    def getArtistLink(self, artist):
    #Retrieve artist link by making a research in parolesmania in http
        '''
        conn = httplib.HTTPConnection(self.WEBSITE)
        conn.request("GET", "/recherche.php?c=artist&k="+urllib.quote(artist))
        reply = conn.getresponse()
        '''
        conn = urllib.urlopen("http://"+self.WEBSITE+"/recherche.php?c=artist&k="+urllib.quote(artist), proxies=self.proxy)
        #reply = conn.info()
        #print reply.status," ",reply.reason #maybe use it for error handling
        #artist_link = reply.getheader("location") #Gather artist link in the location http header
        artist_link = conn.url #Gather artist link in the location http header
        #if artist_link is None:
        if re.search("recherche.php", artist_link):
            #diff_artist_page = reply.read()
            diff_artist_page = conn.read()
            for enc in ('utf8','iso-8859-1','iso-8859-15','cp1252','cp1251','latin1'): #Need to decode the page once downloaded
                try:
                    diff_artist_page = diff_artist_page.decode(enc)
                    break
                except:
                    pass
            self.artist_select_hand = self.ArtistSelectionParser(diff_artist_page,artist) #Create a selection parser to allow the user to choose
            if self.artist_select_hand.found():
                self.log("Perfect Match found, Artist page:"+self.artist_select_hand.getLink()) #Artist is found
                return self.artist_select_hand.getLink()
            else:
                self.artist_selection = self.artist_select_hand.artistlist
                self.log("No perfect match found for "+self.artist)
                return None
        return artist_link

    def resumeSetArtist(self,item): #To call after a setArtist which fail to finalize artist setup
        self.artist_page = self.getArtistPage(self.artist_selection[item][1])
   
    
    def getAvailableArtists(self):#Return the list of available artist to processed in main programm
        return self.artist_selection
    
    def getArtistPage(self, artist_link):
    #Return the HTML content of the artist page
        '''
        conn = httplib.HTTPConnection(self.WEBSITE)
        conn.request("GET", urlparse(artist_link).path) #retrieve the path of the location header to make the new request
        reply2 = conn.getresponse()
        page =  reply2.read()
        '''
        conn = urllib.urlopen("http://"+self.WEBSITE+urlparse(artist_link).path, proxies=self.proxy)
        page = conn.read()
        for enc in ('utf8','iso-8859-1','iso-8859-15','cp1252','cp1251','latin1'): #Need to decode the page once downloaded
            try:
                page = page.decode(enc)
                self.log("Artist Page Encoding : "+enc)
                return page
                break
            except:
                pass
    
    
    def chooseArtist(self): #Just here for the easy method, it just call the choose of the class and finalize artist setup
        self.artist_select_hand.choose()
        if self.artist_select_hand.found():
            self.artist_page = self.getArtistPage(self.artist_select_hand.getLink())
            return True
        else:
            return False  

    #Used to parse the artist page and find the good one in ambiguous artist names
    class ArtistSelectionParser(HTMLParser):#Create our personalized Parser
        def __init__(self,page,who):
            HTMLParser.__init__(self)
            self.page = page
            self.who = who
            
            self.artistlist = list()
            self.final_link = ""
            self.run()
            
        def handle_starttag(self, tag, attrs):
        #Parse HTML Code
            if tag == "a":
                link=""
                for e in attrs:
                    if e[0] == "href":
                        link=e[1]
                    if e[0] == "title" and re.match("^"+self.who+" paroles$", e[1], re.IGNORECASE):
                        self.final_link = link
                        #print "Perfect Artist Match found : ",e[1]
                        break
                    elif e[0] == "title" and re.match(".*"+self.who+".* paroles$", e[1], re.IGNORECASE):
                        self.artistlist.append((re.sub(" paroles$","",e[1]),link))
    
        def choose(self): #Used only in the easy method
            print "0. Skip this Artist"
            for i in range(len(self.artistlist)):
                print i+1,". ",self.artistlist[i][0]
                i = i + 1
            c = raw_input("You choice: ")
            c = int(c)
            if c == 0: self.final_link = None
            try:
                self.final_link = self.artistlist[c-1][1]
            except IndexError:
                print "Bad choice (artist Skipped)"
                self.final_link = None
    
        def found(self):
            return self.final_link != "" and self.final_link is not None
        
        def getLink(self):
            return self.final_link
    
        def run(self):
            self.feed(self.page) #Send content to the parser (launch parsing)
    '''-------------------------------
    ----------------------------------
    -------------------------------'''
  
  
  
    '''----------------------------------
    ------ Song&Lyrics lookup stuff -----
    ----------------------------------'''
    def setTitle(self, song):
    #Once Title receive artist page is parsed to find song URL and then page,lyrics 
        self.title = song
        if self.artist_page is not None:
            self.title_hand = self.SongsParser(self.artist_page,self.title) # call SongParser which gonna parse artist page and ask for title if needed
            if self.title_hand.found():
                self.log("Perfect Match found, song link: "+self.title_hand.getLyricsLink())
                self.setLyrics(self.title_hand.getLyricsLink())
                return True
            else:
                self.title_selection = self.title_hand.titlelist        
                self.log("No perfect match found for"+self.title)
                return None
        else:
            print "Artist not set"
            return False
  
    
    def setLyrics(self,link):
        #maybe check if self.title_page is not None
        ly = self.LyricsParser("http://"+self.WEBSITE+link,self.proxy) #Pick up lyrics in SongParser object 
        self.lyrics = ly.getLyrics()
        
        # try to find the right encoding
        for enc in ('utf8','iso-8859-1','iso-8859-15','cp1252','cp1251','latin1'):
            try:
                self.lyrics = self.lyrics.decode(enc)
                self.log("Encoding found for lyrics: "+enc)
                break
            except:
                pass
            
    def resumeSetTitle(self,item): #To call after a setArtist which fail to finalize artist setup
        self.setLyrics(self.title_selection[item][1])
    
    def getAvailableTitles(self):#Return the list of available artist to processed in main programm
        return self.title_selection                              

    def chooseTitle(self): #Just here for the easy method, it just call the choose of the class and finalize artist setup
        self.title_hand.choose()
        if self.title_hand.found():
            self.setLyrics(self.title_hand.getLyricsLink())
            return True
        else:
            return False  
                                     
    #Used to parse all available song title and find the good one
    class SongsParser(HTMLParser):#Create our personalized Parser
        def __init__(self,page,title):
            HTMLParser.__init__(self)
            self.page = page
            self.title = title
            
            self.titlelist = list()
            self.final_link = ""
            self.run()
            
        def handle_starttag(self, tag, attrs):
        #Parse artist page to find the song link. If ambiguous create a list of songs which matches partially.
            if tag == "a":
                link=""
                for e in attrs:
                    if e[0] == "href":
                        link=e[1]
                    if e[0] == "title" and re.match("^Paroles de "+self.title+"$", e[1], re.IGNORECASE):
                        #print "Perfect Title Match found: ",e[1]
                        self.final_link = link
                    elif e[0] == "title" and re.search("|".join([re.escape(x) for x in self.title.split(" ")]), re.sub("Paroles De ","",e[1]), re.IGNORECASE):
                        self.titlelist.append((re.sub("Paroles De ","",e[1]),link))
    
        def choose(self):
            print "0. Skip this Song"
            for i in range(len(self.titlelist)):
                print i+1,". ",self.titlelist[i][0]
                i = i + 1
            c = raw_input("You choice: ")
            c = int(c)
            if c == 0: self.final_link = None
            try:
                self.final_link = self.titlelist[c-1][1]
            except IndexError:
                print "Bad choice (song skipped)"
                self.final_link = None

        def found(self):
            return self.final_link != "" and self.final_link is not None
            
        def getLyricsLink(self):
            return self.final_link
    
        def run(self):
            self.feed(self.page) #Send content to the parser
            #if self.final_link == "":
            #    self.choose()      
        
        
        
    # Used to parse lyrics within the Lyrics page    
    class LyricsParser(HTMLParser):#Create our personalized Parser
        def __init__(self,url,proxy):
            HTMLParser.__init__(self)
            self.proxy= proxy
            self.url = url
            self.inContent = False
            self.lyrics = ""
            self.run()
            
        def handle_starttag(self, tag, attrs):
            if tag == "div":
                for e in attrs:
                    if e[0] == "id" and e[1] == "songlyrics_h":
                        self.inContent = True
    
        def handle_data(self, data):
            if self.inContent:
                self.lyrics += data
            
        def handle_endtag(self, tag):
            if tag =="div" and self.inContent:
                self.inContent = False
                
        def getLyrics(self):
            return self.lyrics
    
        def run(self):
            data = urllib.urlopen(self.url.encode("utf8"), proxies=self.proxy).read()
            #Grab Web Page Content
            self.feed(data) #Send content to the parser
    '''-------------------------------
    ----------------------------------
    -------------------------------'''