# djboc
Uses Selenium to collect Risk and Compliance documents from Dow Jones' risk database and prepare reports for Bank of China.
## Installation
1. First install the dependencies (`pipenv install --skip-lock`) and make sure a `pdf`folder exists.
2. Download the chromedriver and put it in the directory.
3. Use `pipenv run python creds.py` to create the creds.json file which contains the username and password to the Dow Jones website

## Usage
Simply run
```
pipenv run python dj.py "<name1>" "<name2>" [...]
```
For every given name, this will do the following:
1. Create a PDF and a csv of the search results
2. Download a PDF of an entity if the match percentage is larger than 95. Value can be overriden using the --threshold option. (See `pipenv run python dj.py --help`).

Note that the script can safely be run in parallel. However, I have not tested it with more than two instances.
