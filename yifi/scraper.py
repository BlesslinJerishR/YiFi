import os
import sys
import math
import json
import csv
import requests
from tqdm import tqdm
from fake_useragent import UserAgent
from concurrent.futures.thread import ThreadPoolExecutor


class Scraper:
    """
    Scraper class - Initialized with Keys
    """
    
    # Constructor
    def __init__(self, args):
        self.output = args.output
        self.genre = args.genre
        self.minimum_rating = args.rating
        self.quality = '3d' if (args.quality == '3d') else args.quality
        self.categorize = args.categorize_by
        self.sort_by = args.sort_by
        self.year_limit = args.year_limit
        self.page_arg = args.page
        self.poster = args.background
        self.imdb_id = args.imdb_id
        self.multiprocess = args.multiprocess
        self.csv_only = args.csv_only
        
        self.movie_count = None
        self.url = None
        self.existing_file_counter = None
        self.skip_exit_condition = None
        self.downloaded_movie_ids = None
        self.progress_bar = None
        
        # Output Directory
        if args.output:
            if not args.csv_only:
                os.makedirs(self.output, exist_ok = True)
            self.directory = os.path.join(os.path.curdir, self.output)
        else:
            if not args.csv_only:
                os.makedirs(self.categorize.title(), exist_ok = True)
            self.directory = os.path.join(os.path.curdir, self.categorize.title())
            
        # Keys to Download .torrents in reverse chronological orderorder_order_globs
        if args.sort_by == 'latest':
            self.sort_by = 'date_added'
            self.order_by = 'desc'
        else:
            self.order_by = 'asc'
        
        # yts API - Max get requests 50
        self.limit = 50
    
    # Connect to API & extract initial data
    def __get_api_data(self):
        # Format URL
        url = """https://yts.mx/api/v2/list_movies.json?quality={quality}&genre={genre}&minimum_rating={minimum_rating}&sort_by={sort_by}&order_by={order_by}&limit={limit}&page=""".format(
                 quality = self.quality,
                 genre = self.genre,
                 minimum_rating = self.minimum_rating,
                 sort_by = self.sort_by,
                 order_by = self.order_by,
                 limit = self.limit,          
            )
    
        # Fake User Agent Header ( Random )
        try:
            user_agent = UserAgent()
            headers = {'User-Agent' : user_agent.random}
        except:
            print("Error occured during Fake User Agent Generation.")

        # Connection Errors
        try:
            req = requests.get(url,
                               timeout = 5,
                               verify = True,
                               headers = headers)
            req.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print('HTTP Error : ', errh)
            sys.exit(0)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting : ", errc)
            sys.exit(0)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error : ", errt)
            sys.exit(0)
        except requests.exceptions.RequestException as err:
            print("There was an Error : ", err)
            sys.exit(0)

        # Exception For JSON Handling
        try:
            data = req.json()
        except json.decoder.JSONDecodeError:
            print("Could not decode JSON")

        # Adjust Movie Count accordingly to starting page number
        if self.page_arg == 1:
            movie_count = data.get('data').get('movie_count')
        else:
            movie_count = (data.get('data').get('movie_count')) - ((self.page_arg - 1) * self.limit)

        self.movie_count = movie_count
        self.url = url
    
    def __initialize_download(self):
        # Used for exit/continue prompt that's triggered after 10 existing files
        self.existing_file_counter = 0
        self.skip_exit_condition = False
        
        # YTS Dupes
        # More > 1x
        # IDs are stored in this array
        # To Check File is downloaded before
        self.downloaded_movie_ids = []
        # Calc Page Count !x = 1 to except range(1, 1)
        if math.trunc(self.movie_count / self.limit) + 1 == 1:
            page_count = 2
        else:
            page_count = math.trunc(self.movie_count / self.limit) + 1

        range_ =  range(int(self.page_arg), page_count)
        
        print("Initializing download with these Keys : \n")
        print("")
        print(f"""Folder: {self.directory}
                 Quality: {self.quality}
                 Genre: {self.genre} 
                 Min Rating: {self.minimum_rating}
                 Categorization: {self.categorize}
                 Page: {self.page_arg}
                 Cover: {self.poster}
                 IMDB: {self.imdb_id}
                 Multi-Threading: {self.multiprocess}
                 """)
        
        if self.movie_count <= 0:
            print("Could not find any movies with given Keywords")
            sys.exit(0)
        else:
            print(".torrentz automation successful .")
            print(f"Found {self.movie_count} movies. Starting Download ...")
            
        # Progress background
        self.progress_bar = tqdm(total = self.movie_count, 
                                 position = 0,
                                 leave = True,
                                 desc = "Downloading",
                                 unit = 'Files')
        
        # MultiProcess Executor
        # max_workers to None = Executor Utilize CPU * 5 @
        executor = ThreadPoolExecutor(max_workers = None)
        for page in range_:
            url = "{}{}".format(self.url, str(page))
            # Generate Random User Fake User Agent
            try:
                user_agent = UserAgent()
                headers = {'User_Agent': user_agent.random}
            except:
                print("Error Occured During Fake user Gen.")
                
            # API request
            page_response = requests.get(url, 
                                         timeout = 5, 
                                         verify = True, 
                                         headers = headers).json()
            
            movies = page_response.get('data').get('movies')
            
            # print(movies)
            # Movies on Current Page
            if not movies:
                print("Could not find any .torrentz on this page.\n")
            
            if self.multiprocess:
                #  wrap tqdm arounD executor to update progress_bar with every MultiProcess
                tqdm(executor.map(self.__filter_torrents, movies), 
                     total = self.movie_count,
                     position = 0,
                     leave = True)
                
            else:
                for movie in movies:
                    self.__filter_torrents(movie)
            
        self.progress_bar.close()
        print("Download Finished")
        
    
    # .torrent file selector for downloading
    def __filter_torrents(self, movie):
        movie_id = str(movie.get('id'))
        movie_rating = movie.get('rating')
        movie_genres = movie.get('genres') if movie.get('genres') else ['None']
        movie_name_short = movie.get('title')
        imdb_id = movie.get('imdb_code')
        year = movie.get('year')
        language = movie.get('language')
        yts_url = movie.get('url')
        
        if year < self.year_limit:
            return
        
        # .torrent option for current movie 
        torrents = movie.get('torrents')
        # reformat names
        movie_name = movie.get('title_long').translate({ord(i): None for i in "'/\:*?<>|"})
        # Multi Folder Categorization
        
        is_download_successful = False
        if movie_id in self.downloaded_movie_ids:
            return
        
        # 0 .torrentz available        
        if torrents is None:
            tqdm.write(f"Could not find any torrents for {self.movie_name}. Skipping ...")
            return
        
        bin_content_img = (requests.get(movie.get('large_cover_image'))).content if self.poster else None
        
        # Iterate through available torrent files
        for torrent in torrents:
            quality = torrent.get('quality')
            torrent_url = torrent.get('url')
            if self.categorize and self.categorize != 'rating':
                if self.quality == 'all' or self.quality == quality:
                    bin_content_tor = (requests.get(torrent.get('url'))).content
                    
                    for genre in movie_genres:
                        path = self.__build_path(movie_name, movie_rating, quality, genre, imdb_id)
                        is_download_successful = self.__download_file(bin_content_tor, bin_content_img, path, movie_name, movie_id)   
            else:
                if self.quality == 'all' or self.quality == quality:
                    self.__log_csv(movie_id, imdb_id, movie_name_short, year, language, movie_rating, quality, yts_url, torrent_url)
                    bin_content_tor = (requests.get(torrent_url)).content
                    path = self.__build_path(movie_name, movie_rating, quality, None, imdb_id)          
                    is_download_successful = self.__download_file(bin_content_tor, bin_content_img, path, movie_name, movie_id)

            if is_download_successful and self.quality == 'all' or self.quality == quality:
                tqdm.write("Downloaded {} {}".format(movie_name, quality.upper()))
                self.progress_bar.update()
                
    # Creates a file path for each download
    def __build_path(self, movie_name, rating, quality, movie_genre, imdb_id):
        if self.csv_only:
            return
        
        directory = self.directory
        
        if self.categorize == "rating":
            directory += "/" + str(math.trunc(rating)) + "+"
        elif self.categorize == "genre":
            directory += "/" + str(movie_genre)
        elif self.categorize == "rating-genre":
            directory += "/" + str(math.trunc(rating)) + "+/" + movie_genre
        elif self.categorize == "genre-rating":
            directory += "/" + str(movie_genre) + "+/" + str(math.trunc(rating)) + "+"
        
        if self.poster:
            directory += "/" + movie_name
            
        os.makedirs(directory, exist_ok = True)
        
        if self.imdb_id:
            filename = f"{movie_name} {quality} - {imdb_id}"
        else:
            filename = f"{movie_name} {quality}"
            
        path = os.path.join(directory, filename)
        return path
    # .bin to .torrent
    def __download_file(self, bin_content_tor, bin_content_img, path, movie_name, movie_id):
        if self.csv_only:
            return
        
        if self.existing_file_counter > 10 and not self.skip_exit_condition:
            self.__prompt_existing_files()
        
        if os.path.isfile(path):
            tqdm.write(f"{movie_name} - File already exists. Skipping ...")
            self.existing_file_counter += 1
            return False
        
        with open(path + ".torrent", "wb") as torrent:
            torrent.write(bin_content_tor)
        if self.poster:
            with open(path + ".jpg", "wb") as torrent:
                torrent.write(bin_content_img)
        
        self.downloaded_movie_ids.append(movie_id)
        self.existing_file_counter = 0
        return True
    
    def __log_csv(self, id, imdb_id, name, year, language, rating, quality, yts_url, torrent_url):
        path = os.path.join(os.path.curdir, "YiFi-Scraper.csv")
        csv_exists = os.path.isfile(path)
        
        with open(path, mode='a') as csv_file:
            headers = ['YTS ID', 'IMDB ID', 'Movie Title', 'Year', 'Language', 'Rating', 'Quality', 'YTS URL', 'IMDb URL', 'Torrent URL']
            writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=headers)
            
            if not csv_exists:
                writer.writeheader()
            
            writer.writerow({'YTS id' : id, 
                            'IMDB id' : imdb_id,
                            'Year' : year,
                            'Language': language,
                            'Rating' : rating,
                            'Quality' : quality,
                            'YTS url' : yts_url,
                            'IMDB url' : 'https://www/imdb.com/title/' + imdb_id,
                            'Torrent url': torrent_url
                            })
            
            
    def __prompt_existing_files(self):
        tqdm.write("Found 10 existing files . Do you want to keep downloading ? [ Y or N ]  : ")                    
        exit_answer = str(input())
        
        if exit_answer.lower() == 'n':
            tqdm.write("Self Distructing")
            sys.exit(0)
        elif exit_answer.lower() == 'y':
            tqdm.write("Dowloading with Prayers")
            self.existing_file_counter = 0
            self.skip_exit_condition = True
        else:
            tqdm.write("Invalid Input Enter only Y or N")
    
    def download(self):
        self.__get_api_data()
        self.__initialize_download()
            
            
            
            