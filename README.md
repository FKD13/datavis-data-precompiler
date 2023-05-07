# Data Precompiler

Generate json based on raw csv files.

Will generate the following API structure:

- `/compiled_data/{series}/all.json`: All data on a specific series
- `/compiled_data/{series}/year/{year}.json`: All data of a particular year for a series.

## Installing

```bash
asdf install
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirenments.txt
```

## Running

```bash
python3 compile.py
```
