# Generate Anki deck with translations and definitions from list of words

## TODO
* clean up code
* better error handling
* better fetching for Bab.la
* more readable card formatting
* some way of automatically synchronising with my phone
* better handling of special cases (definition not found, incorrect word)
* distinction between definitions shown on the front and the back (eg. not showing the word in definitions)
* ~~add Merriam-Webster fetching~~
* add comments (for example usage, and just for comments)
* add direct input, defining words in the text file
* add sentences without definitions, eg. stylistically pleasing wording that you understand, but want to remember
* handle what happens when the parser find some unexpected page - currently an error occurs
* add some memorization/caching, since an error in the middle of 10 minute session is currently really annoying
* empty lines in the vocab file currently break parser