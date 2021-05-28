# list-csv

get list tag(ul, ol) sentence from url.

## Getting Started

First, install requirements

```s
pip install -r requirements.txt
```

Then, do run main.py.

```s
python3 main.py <input filename> <tag> <output filename>
```

Current, program runs only for ul and ol tag.

`input filename` must be a file with urls.

For example:

```s
python3 main.py wiki_urls.txt ul result.txt
```

## Results

csv files with such format:

```s
<url>,<original text>,<previous text>
```

see [result](/result).
