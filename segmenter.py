# -*- coding: utf-8 -*-
import wordsegment as ws


class Segmenter():
    """A class for managing segmentation of input strings."""
    
    def __init__(self):
        ws.load()

    def segment(self, text):
        return ws.segment(text)