"""
    Dec 12, 2017

    simple reddit bot that response with a comment when
    a certain phrase is found in a reddit comment
"""

import os
import praw
import re
import time

# known exceptions
from praw.exceptions import APIException
from prawcore import Forbidden


class GrammarBot:
    # data stored in txt files
    FILE_NAME = {"id": "text_files/comment_id.txt",
                 "name": "text_files/comment_author.txt",
                 "phrases": "text_files/correct_word.txt"}
    # subreddit to search
    SUBREDDIT = 'test'
    # keep track of comments replied too
    comment_id = []
    # keep track of users replied too
    comment_author = []
    # phrases bot should look for
    phrases = dict()
    # reddit log-in authentication
    reddit = None

    #
    def __init__(self):
        # set all authentication info
        self.reddit = self.authenticate()
        # keep track of number of checks
        self.iteration = 0
        # get phrases to look for
        self.phrases = self.get_phrase_dict()
        # create a list of comment.id that bot already responded too
        self.comment_id = self.get_list_from_file(self.FILE_NAME["id"])
        # create a list of comment.author that bot already responded too
        self.comment_author = self.get_list_from_file(self.FILE_NAME["name"])

    # all the login info for bot
    @staticmethod
    def authenticate():
        reddit = praw.Reddit('bot')
        print("authenticated as {}".format(reddit.user.me()))
        return reddit

    #
    @staticmethod
    def get_list_from_file(file):
        if os.path.isfile(file):
            with open(file, "r") as fl:
                return fl.read().split("\n")
        else:
            return None

    #
    @staticmethod
    def append_to_file(file, value):
        if os.path.isfile(file):
            with open(file, "a") as fl:
                fl.write(value + "\n")

    # opens a text file and parses it into dict format
    def get_phrase_dict(self):
        phrases = self.get_list_from_file(self.FILE_NAME["phrases"])
        phrase_dict = dict()
        # parse phrases into dict format
        for phrase in phrases:
            phrase = phrase.split(":")
            phrase_dict.update({phrase[0]: phrase[1]})

        return (phrase_dict)

    # search through a subreddit comments, checks for a phrase, responds to set phrase
    def check_comments(self, authenticated, comment_id, comment_author):

        try:
            print("check comments")
            # collect comments from a subreddit 100 max as per reddit
            for comment in authenticated.subreddit(self.SUBREDDIT).comments(limit=100):
                # multiple phrases checked
                for key, value in self.phrases.items():
                    # check if comment has a mistake with regex
                    contains_phrase = re.search(r"\b{}\b".format(key), comment.body.lower())
                    # phase found and its new, not posted by self
                    if contains_phrase and comment.id not in comment_id and \
                            not comment.author == authenticated.user.me():
                        # this is the code that responds to comment
                        comment.reply(">. . . ¿ {} ? . . . \n\nI THINK YOU MEANT **{}**"
                                      "\n\n\n\n\n\n^^I ^^AM ^^A ^^BOT^^^beep^boop!"
                                      .format(key, value))
                        # updates the list of comment id
                        self.comment_id.append(comment.id)
                        self.append_to_file(self.FILE_NAME["id"], comment.id)
                        # if author is not in the list add it to the list
                        if str(comment.author) not in comment_author:
                            comment_author.append(str(comment.author))
                            self.append_to_file(self.FILE_NAME["name"], str(comment.author))
                        #
                        print("\n{} found in {} by {}\n"
                              .format(key, str(comment.id), str(comment.author)))

            # put bot to sleep 2 sec minimum
            print("sleep")
            time.sleep(5)

        # current known exceptions to catch
        except APIException as e:
            print("api exception {}".format(e))
        except Forbidden as e:
            print("forbidden exception {}".format(e))

    # main method
    def run_bot(self):
        # run forever as long as authentication is valid
        while True and self.reddit is not None:
            self.check_comments(self.reddit, self.comment_id, self.comment_author)
            self.iteration += 1
            #
            print("round {}".format(self.iteration))
            print("{} comments replied too\n".format(len(self.comment_id)))


bot = GrammarBot

if __name__ == "__main__":
    bot().run_bot()