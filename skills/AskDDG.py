import os
import typing
import logging
import requests
import string
import nltk
import os
import math
import re
import glob
from utils.speak import say_text
from bs4 import BeautifulSoup
from skills.Skill import Skill

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AskDDG(Skill):

    MAX_RESULTS = 10
    MATCHES = 1
    SENTENCES = 2
    DO_QUERY = r"^(busca|dime).+$"
    BASE_URL = "https://html.duckduckgo.com/html/"

    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        if re.match(AskDDG.DO_QUERY, transcript):
            query = transcript.replace('dime', '').replace('busca', '').strip()
            params = {
                "q": f"{query}?"
            }
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(AskDDG.BASE_URL, params=params, headers=headers)
            soup = BeautifulSoup(response.text, features="lxml")
            results = soup.find_all('a', {"class": "result__snippet"})
            for idx, res in enumerate(results):
                if idx > AskDDG.MAX_RESULTS:
                    break
                with open(f"{idx}_doc.txt", "w") as f:
                    f.write(res.get_text())

            files = self.load_files(".")
            file_words = {
                filename: self.tokenize(files[filename])
                for filename in files
            }
            file_idfs = self.compute_idfs(file_words)
            query = self.tokenize(query)
            filenames = self.top_files(query, file_words, file_idfs, n=AskDDG.MATCHES)
            # Extract sentences from top files
            sentences = dict()
            for filename in filenames:
                for passage in files[filename].split("\n"):
                    for sentence in nltk.sent_tokenize(passage):
                        tokens = self.tokenize(sentence)
                        if tokens:
                            sentences[sentence] = tokens

            # Compute IDF values across sentences
            idfs = self.compute_idfs(sentences)

            # Determine top sentence matches
            matches = self.top_sentences(query, sentences, idfs, n=AskDDG.SENTENCES)
            for match in matches:
                say_text(match)
            for f in glob.glob('*doc.txt'):
                os.remove(f)
            return True, AskDDG.DO_QUERY
        return False, transcript

    def load_files(self, directory):
        """
        Given a directory name, return a dictionary mapping the filename of each
        `.txt` file inside that directory to the file's contents as a string.
        """
        files = dict()
        for filename in glob.glob('*doc.txt'):
            with open(os.path.join(directory, filename), encoding="utf8") as f:
                files[filename] = f.read()
        return files

    def tokenize(self, document):
        """
        Given a document (represented as a string), return a list of all of the
        words in that document, in order.

        Process document by coverting all words to lowercase, and removing any
        punctuation or English stopwords.
        """
        return [word.lower() for word in nltk.word_tokenize(document) 
            if word.lower() not in nltk.corpus.stopwords.words("spanish") 
            and word not in string.punctuation]


    def compute_idfs(self, documents):
        """
        Given a dictionary of `documents` that maps names of documents to a list
        of words, return a dictionary that maps words to their IDF values.

        Any word that appears in at least one of the documents should be in the
        resulting dictionary.
        """
        idfs = dict()
        for document in documents:
            for word in documents[document]:
                f = sum(word in documents[filename] for filename in documents)
                idf = math.log(len(list(documents.keys())) / f)
                idfs[word] = idf
        return idfs

    def top_files(self, query, files, idfs, n):
        """
        Given a `query` (a set of words), `files` (a dictionary mapping names of
        files to a list of their words), and `idfs` (a dictionary mapping words
        to their IDF values), return a list of the filenames of the the `n` top
        files that match the query, ranked according to tf-idf.
        """
        word_frequencies = dict()
        for filename in files: #calculate word frequency from query that appears in files
            word_frequencies[filename] = dict()
            for word in files[filename]:
                if word in query and word in idfs:
                    if word not in word_frequencies[filename]:
                        word_frequencies[filename][word] = 1
                    else:
                        word_frequencies[filename][word] += 1
        tfidfs = dict()
        for filename in word_frequencies: #calculate tfidf of recolected words
            tfidfs[filename] = 0
            for word, tf in word_frequencies[filename].items():
                tfidfs[filename] += tf * idfs[word]
        tfidfs = {k: v for k, v in sorted(tfidfs.items(), key=lambda item: item[1], reverse=True)}
        return list(tfidfs.keys())[:n]


    def top_sentences(self, query, sentences, idfs, n):
        """
        Given a `query` (a set of words), `sentences` (a dictionary mapping
        sentences to a list of their words), and `idfs` (a dictionary mapping words
        to their IDF values), return a list of the `n` top sentences that match
        the query, ranked according to idf. If there are ties, preference should
        be given to sentences that have a higher query term density.
        """
        sentence_rank = dict()
        term_density = dict()
        for sentence in sentences:
            term_density[sentence] = 0
            sentence_rank[sentence] = 0
            for word in query:
                if word in sentences[sentence]:
                    sentence_rank[sentence] += idfs[word]
            for word in sentences[sentence]:
                if word in query:
                    term_density[sentence] += 1
            term_density[sentence] /= len(sentence.split(" "))
        sentence_rank = {k: v for k, v in sorted(sentence_rank.items(), key=lambda item: item[1], reverse=True)}
        top_sentences = list(sentence_rank.keys())
        for i, s1 in enumerate(sentence_rank.keys()):
            for s2 in list(sentence_rank.keys())[i+1:]:
                if sentence_rank[s1] == sentence_rank[s2]:
                    if term_density[s1] < term_density[s2]:
                        tmp_sentence = top_sentences[i]
                        top_sentences[i] = top_sentences[i+1]
                        top_sentences[i+1] = tmp_sentence
        return top_sentences[:n]
