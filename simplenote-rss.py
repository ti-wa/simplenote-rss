#!/usr/bin/env python
import simplenote
import feedparser
import string
import sys
import os
import ConfigParser
import time

sleepSeconds = False
verbose = False
debug = False

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
            
            
def newFeedEntrysToSimpleNote(tag,feedUrl):
    if(verbose):
        print "Create notes for: " + feedUrl + " with tag: " + tag
    note_keys_with_tag_list = list()
    notes_with_tag_tuple = simplenote.get_note_list(tags=[tag])
    notes_with_tag_list = notes_with_tag_tuple[0]
    for item in notes_with_tag_list:
        item = str(item)
        key_start_index = string.find(item,"'key'")
        item = item[key_start_index+9:]
        key_end_index = string.find(item,"'")
        item = item[:key_end_index]
        note_keys_with_tag_list.append(item)
    notes_with_tag_list = str()
    for key in note_keys_with_tag_list:
        notes_with_tag_list += str(simplenote.get_note(key))
    feed = feedparser.parse(feedUrl)
    if(debug):
        print feed
    if(feed.status != 200):
        print "http-code " + feed.status + " in feed " + tag
        print "cancel creating notes  for " + feedUrl 
        return None
    for post in feed.entries:
        if string.find(notes_with_tag_list,post.link) != -1:
            if(verbose):
                print post.link + " not added"
            continue
        note_content = post.title + "\n" + post.link +"\n"
        note = {"content":note_content.encode("utf-8") , "tags": [tag] }
        if(verbose):
            print post.link + " added" 
        if(not(debug)):
            simplenote.add_note(note)
     
        
        
args = sys.argv[1:]
while len(args):
    if args[0] == "-h":
        print "-p minutes     pause between to pools. You should use a Cron Job for this Script"
        print "-v             verbose mode on"
        print "-d             debug mode on"
        exit()
    if args[0] == "-p":
        if len(args) < 2:
            exit()
        if  not(args[1].isdigit()):
            print "no minutes parameter after -p"
            exit()
        sleepSeconds = float(args[1]) * 60 
        args = args[2:]
        continue
    if args[0] == "-v":
        args = args[1:]
        verbose = True
        continue
    if args[0] == "-d":
        args = args[1:]
        verbose = True
        debug = True
        continue

current_file_dir = os.path.dirname(__file__)
other_file_path = os.path.join(current_file_dir, "simplenote-rss.ini")
Config = ConfigParser.ConfigParser()
Config.read(other_file_path)
sections = Config.sections()

mail = ConfigSectionMap("Credentials")["mail"]
password = ConfigSectionMap("Credentials")["password"]
simplenote = simplenote.Simplenote(mail,password)


if(verbose and sleepSeconds):
    print "Programm runs every " + str(int(sleepSeconds)) + " seconds"

while True:
    for section in sections:
        if "feed" in section.lower():
            tag = ConfigSectionMap(section)["tag"]
            feedUrl= ConfigSectionMap(section)["url"]
            newFeedEntrysToSimpleNote(tag,feedUrl)
    if not(sleepSeconds):
        exit()    
    if(verbose and sleepSeconds):
        print "Next poll in " + str(int(sleepSeconds)) + " seconds"
    time.sleep(sleepSeconds)


