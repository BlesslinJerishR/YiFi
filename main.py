import argparse
import traceback

def main():
    """YiFi - .torrent database downloader for
       Web Appplication ( yts.com ) 
    """
    
    desc = "YiFi - .torrent database downloader for yts.com"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('o', 'output',
                        help = 'Directory',
                        dest = 'output',
                        type = str.lower,
                        required = False)
    
    parser.add_argument('-q', 'quality',
                        help = """
                        Torrent Quality . Valid Arguments are :
                        'all',
                        '720p',
                        '1080p',
                        '3d',
                        """,
                        dest = 'quality',
                        type = str.lower,
                        required = False,
                        choices = ['all', '720p', '1080p', '3d'],
                        default = '1080p',
                        const = '1080p',
                        nargs = '?'
                        )
    
    parser.add_argument('-g', '--genre',
                        help="""
                        Movie Genre : Valid Arguments are : "all", "action", "adventure",
                                                     "animation", "biography", "comedy",
                                                     "crime", "documentary", "drama", "family",
                                                     "fantasy", "film-noir", "game-show", "history",
                                                     "horror", "music", "musical", "mystery", "news",
                                                     "reality-tv", "romance", "sci-fi", "sport",
                                                     "talk-show", "thriller", "war", "western",
                        """,
                        dest = 'genre',
                        type = str.lower,
                        required = False,
                        choices = ['all', 'action', 'adventure', 'animation', 'biography',
                                 'comedy', 'crime', 'documentary', 'drama', 'family',
                                 'fantasy', 'film-noir', 'game-show', 'history', 'horror',
                                 'music', 'musical', 'mystery', 'news', 'reality-tv', 'romance',
                                 'sci-fi', 'sport', 'talk-show', 'thriller', 'war', 'western'],
                        default = 'all',
                        const = 'all',
                        nargs = '?'
                        )
    
    parser.add_argument('-c', '--categorizer',
                        help = """/folder structure.
                                    >Valid arguments are: "rating", "genre",
                                     "rating-genre","genre-rating"
                        """,
                        dest = 'categorize',
                        type = str.lower,
                        required = False,
                        choices = ['none', 'rating', 'genre', 'genre-rating', 'rating-genre'],
                        default = 'rating',
                        const = 'rating',
                        nargs = '?'
                        )
    
    parser.add_argument('-i', '--imdb',
                        help = 'append -i to append IMDB ID to filename.',
                        dest = 'imdb',
                        type = bool,
                        required = False,
                        default = False,
                        const = True,
                        nargs = '?'
                        )
    
    parser.add_argument('-m', '--multiprocess',
                        help = """
                            append -m to download using multiprocessor.
                                This option makes the process significantly faster
                                but is prone to raising flags and causing server to deny requests.
                        """,
                        dest='multiprocess',
                        type = bool,
                        required = False,
                        default = False,
                        const = True,
                        nargs = '?'
                        )
    
    parser.add_argument('--csv',
                        help = """
                            append --csv to log scraped data ONLY to a CSV file.
                                With this argument .torrent files will not be downloaded
                        """,
                        dest = 'csv',
                        type = bool,
                        required = False,
                        default = 1,
                        const = 1,
                        nargs = '?'
                        )

    parser.add_argument('-p', '--page',
                        help='Enter a page number to skip ahead number of pages',
                        dest='page',
                        type = int,
                        required = False,
                        default = 1,
                        const = 1,
                        nargs = '?'
                        )
    
    try:
        args = parser.parse_args()
        scraper = Scraper(args)
        scaper.download()
    except KeyboardInterrupt:
        print("\n Key Interuptions , Exiting with Exitement \n")
    except Exception:
        traceback.print_exc()
    exit()
    
if __name__ == '__main__':
    main()