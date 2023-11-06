# google-map-reviews-scraper


This script automates the process of scraping reviews from Google Maps for various pub locations.

## Features

- Scrapes reviews based on sorting options (relevant, newest, highest rating, lowest rating).
- Downloads associated images of reviews.
- Saves reviews data in CSV format.
- Deduplicates and merges all reviews from different sorting options.

## Prerequisites

- Python 3.x
- Selenium WebDriver
- ChromeDriver (compatible with the installed Chrome version)

## Installation

Clone this repository to your local machine:

https://github.com/timadeg/google-map-reviews-scraper

cd pub-reviews-scraper


Install the required packages:

pip install -r requirements.txt


## Usage

Update the `london pubs2.csv` file with the list of pubs and their corresponding Google Maps URLs.

Run the script:

python pub_reviews_scraper.py


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
