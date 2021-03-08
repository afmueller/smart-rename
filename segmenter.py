# -*- coding: utf-8 -*-
import wordsegment as ws


class Segmenter():
    """A class for managing segmentation of input strings."""
    
    def __init__(self, ngrams=None):
        ws.load()
        
        # add unigrams to wordsegment defaults
        if ngrams and 'unigrams' in ngrams:
            for ngram, count in ngrams['unigrams'].items():
                ws.UNIGRAMS[ngram] = count

        # add bigrams to wordsegment defaults
        if ngrams and 'bigrams' in ngrams:
            for ngram, count in ngrams['bigrams'].items():
                ws.BIGRAMS[ngram] = count

    def segment(self, text):
        return ws.segment(text)