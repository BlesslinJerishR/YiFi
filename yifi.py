import os
import sys
import math
import json
import csv
import requests
from tqdm import tqdm
from fake_useragent import UserAgent
import concurrent.futures.thread import ThreadPoolExecutor

class Scraper(object):
    """Scraper class - Initialized with Keys"""
    
    # Constructor
    def __init__(self, args):
        self.output = args.output
        self.genre = args.genre
        self.minimum_rating = args.rating
        self.quality = '3d' if args.quality == '3d' else args.quality
        self.categorize = args.categorize
        self.sort_by = args.sort_by
        self.year_limit = args.year_limit
        self.page_arg = args.page_arg
        self.poster = args.background
        self.imdb_id = args.imdb_id
        self.multiprocess = args.multiprocess
        self.csv = args.csv
        
        self.movie_count = None
        self.url = None
        self.existing_file_counter = None
        self.skip_exit_condition = None
        self.downloaded_movie_ids = None
        self.pbar = None
        
        # Output Directory
        if args.output:
            if not args.csv:
                os.makedirs(self.output, exist_ok = True)
            self.directory = os.path.join(os.path.curdir, self.output)
        else:
            if not args.csv:
                os.makedirs(self.categorize.title(), exist_ok = True)
            self.directory = os.path.join(os.path.curdir, self.categorize.title())
            
        # Keys to Download .torrents in reverse chronological orderorder_order_globs
        if args.sortings == 'latest':
            self.sortings ='date_added'
            self.order_by == 'description'
        else: 
            self.order_by = 'asc'
        
        # yts API - Max get requests 50
        self.limit = 50
    
    # Connect to API & extract initial data
        