from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

import csv
import time 
import random 

LONGITUDES = []
LATITUDES = []

fieldnames = ['longitude', 'latitude']
json_data = 0

with open('data.csv', 'w') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
    csv_writer.writeheader()


import os
from pickle import dump, load

import nltk
from nltk.corpus import brown
from itertools import dropwhile

class Tagfunction:
    def __init__(self):
        if os.path.exists("tagger.pkl"):
            with open('tagger.pkl', 'rb') as data:
                tagfunction = load(data)
            self.tagfunction = tagfunction
        else:
            tagfunction = generate_tagger()
            self.tagfunction = tagfunction
            self.save()

    def save(self):
        with open('tagger.pkl', 'wb') as output:
            dump(self.tagfunction, output, -1)

    def tag(self, sent):
        return self.tagfunction.tag(sent)

    def sentence_tagger(self, sent):
        #Input a sentence in the form of a string to output a list of tuples
        tokenator = nltk.word_tokenize(sent)
        return self.tag(tokenator)

    def is_active(self, sent):
        return is_active(self, sent)

def activep(tags):

    BElist = list(dropwhile(lambda tag: not tag.startswith("BE"), tags))
    GerundNot = lambda tag: tag.startswith("V") and not tag.startswith("VBG")

    filterlist1 = filter(GerundNot, BElist)
    out = any(filterlist1)

    return not out

def generate_tagger():

    train_sents = brown.tagged_sents()


    t0 = nltk.RegexpTagger(
        [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'), # cardinal numbers
         (r'(The|the|A|a|An|an)$', 'AT'), # articles
         (r'.*able$', 'JJ'),              # adjectives
         (r'.*ness$', 'NN'),              # nouns formed from adjectives
         (r'.*ly$', 'RB'),                # adverbs
         (r'.*s$', 'NNS'),                # plural nouns
         (r'.*ing$', 'VBG'),              # gerunds
         (r'.*ed$', 'VBD'),               # past tense verbs
         (r'.*', 'NN')                    # nouns (default)
        ])
    t1 = nltk.UnigramTagger(train_sents, backoff=t0)
    t2 = nltk.BigramTagger(train_sents, backoff=t1)
    t3 = nltk.TrigramTagger(train_sents, backoff=t2)
    return t3
# https://www.nltk.org/book/ 
# Taken from the NLTK book with the purpose of training the data. Not our code.

def is_active(tagfunction, sent):
    tagged = tagfunction.sentence_tagger(sent)
    tags = map(lambda tup: tup[1], tagged)
    return bool(activep(tags))

if __name__ == '__main__':
    t = Tagfunction()
    #assert t.is_active('Mistakes were made.')
    #assert not t.is_active('I made mistakes.')
    # Noteable fail case. Fix me. I think it is because the 'to be' verb is
    # omitted.
    #assert t.is_passive('guy shot by police')


import matplotlib.pyplot as plt 

def save(list_long_lat):
    with open('data.csv', 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = fieldnames)

        info  = {
        'longitude': list_long_lat[0],
        'latitude': list_long_lat[1]
        }

        csv_writer.writerow(info)
        print(list_long_lat[0], list_long_lat[1]) 
        return True

def triangulate(coordinates):
    better_list = coordinates[0]
    lon = (better_list[0][0] + better_list[2][0])/2
    lat = (better_list[0][1] + better_list[1][1])/2
    LONGITUDES.append(lon)
    LATITUDES.append(lat)
    a = [lon,lat]
    return a

def clean_data(json_data):
    keys = list(json_data.keys()) 
    if 'text' and 'place' and 'in_reply_to_status_id' in keys and 'retweeted_status' not in keys:
        Text = json_data['text']
        if Text[:2] != "RT" and json_data["place"] != None and json_data['in_reply_to_status_id'] != None:
            keys_in_place = list(json_data["place"].keys())
            if 'bounding_box' in keys_in_place:
                print(json_data["place"]["bounding_box"]["coordinates"])
                if json_data["truncated"] == True:
                    list_of_coords = json_data["place"]["bounding_box"]["coordinates"]
                    coordinates_imp = triangulate(list_of_coords)
                    #graph(LONGITUDES, LATITUDES)
                    print(json_data["extended_tweet"]["full_text"])
                    
                else: 
                    list_of_coords = json_data["place"]["bounding_box"]["coordinates"]
                    coordinates_imp = triangulate(list_of_coords)
                    #graph(LONGITUDES, LATITUDES)
                    print(json_data["text"])
                
                return coordinates_imp
    return "no"


import Credentials 
 
class StdOutListener(StreamListener):
    def on_status(self, status):
        if status.place != None:
            print(status.text)
            print(status.place)
            print(status)
            print("")

    def on_data(self, data):
        #print(data)#used for cleaning and understanding 

        json_data = json.loads(data)
        final_coords = clean_data(json_data)
        if final_coords != "no":             
            save(final_coords)
        return True
    def on_error(self, status):
        print(status)


if __name__ == "__main__":
    listener = StdOutListener()
    auth = OAuthHandler(Credentials.CONSUMER_KEY, Credentials.CONSUMER_SECRET)
    auth.set_access_token(Credentials.ACCESS_TOKEN, Credentials.ACCESS_TOKEN_SECRET)

    stream = Stream(auth, listener)

    stream.filter(track = ['cornona', 'COVID', 'COVID-19', 'virus', 'coronavirus', 'symptoms','deaths','quaratine', 'lockdown','dry thorat', 'fever', 'Wuhan', 'a' ,'the' ,'he', 'what', 'why', 'when'])
#['chill', 'common cold', 'commoncold', 'flu', 'headcold', 'head cold', 'influenza', 'acute rhinitis', 'acuterhinitis', 'cold', 'sick', 'sneeze', 'sneezing', 'blow nose', 'rhinovirus', 'viral', 'running nose', 'runningnose', 'nasal spray', 'nasalspray', 'expectorants', 'sore throat', 'sorethroat', 'runny nose', 'nasal strips']    
            