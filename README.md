# djboc
Uses Selenium to collects Risk and Compliance documents from Dow Jones' risk database and prepare reports for Bank of China.
## Usage
First install the dependencies (`pipenv install --skip-lock`) and make sure a `pdf`folder exists. Download the chromedriver and put it in the directory. Then simply run
```
pipenv run python dj.py "<name1>" "<name2>" [...]
```
For every given name, this will do the following:
1. Create a PDF and a csv of the search results
2. Download a PDF of an entity if the match percentage is larger than 95. Value can be overriden using the --threshold option. (See `pipenv run python dj.py --help`).

Note that the script can safely be run in parallel. However, I have not tested it with more than two instances.
