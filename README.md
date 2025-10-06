# top20-fimi-downloader

A Python tool to download the latest Top 100 FIMI Italian Singles Chart and save it as an Excel or CSV file.

## Features

- Scrapes the official FIMI chart website for the latest singles ranking.
- Lets you choose how many top entries to save (1–100).
- Saves the chart as `.xlsx` or `.csv` via a graphical file dialog.
- Headless browser automation (no browser window pops up).

## Requirements

- Python 3.8+
- Google Chrome
- [ChromeDriver](https://chromedriver.chromium.org/) (already included in `chromedriver/`)

Python packages (see `requirements.txt`):

- `selenium`
- `bs4`
- `pandas`
- `tkinter`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

1. Make sure Chrome and ChromeDriver are installed and compatible.
2. Run the script:
   ```bash
   python main.py
   ```
3. Enter how many top singles you want to save (1–100).
4. Choose where to save the file and the format (Excel or CSV).

## Notes

- The script uses a GUI dialog for input and file saving.
- The chart is scraped from [FIMI's official website](https://www.fimi.it/top-of-the-music/classifiche/).
- For issues with ChromeDriver, ensure it matches your Chrome version.
