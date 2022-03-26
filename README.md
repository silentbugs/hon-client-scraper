# HoN Client Scraper

This set of messy python scripts fetch data from HoN's public servers.
Used Wireshark to figure out the requests being made.

## How to use

- Requires Python3 (any version should work, written in Python 3.10.2).
- Create a virtualenv (python -m venv ~/.venvs/hon-client-scraper/) and run `pip install -r requirements.txt`
- Run `python main.py --help` to  get a list of arguments
- Example execution: `python main.py -sv 3.3.5 -o wac -a i686`

## Flow

1. Create required directories
2. Fetch zipped manifest file
3. Extract the file inside the specific version
4. Iterate through the XML manifest file and fetch each child `file`
5. Skip already downloaded files.

The manifest file also contains `checksum`, `zipsize` and `filesize` attributes. While in most cases they match, a lot of false mismatches were appearing so there's no checking functionality.

## Parameters

`os`: The operating system. Available options are:

- wac (Windows)
- mac (MacOS)
- linux

`arch`: The architecture

- i686
- x86_64

`version` The client's version. It adheres to semver. Even though a lot of the code uses 4 digit version of semver (e.g. `2.6.35.1`) in most cases when the 4th digit is `0` then the semver gets truncated to a 3 digit one.

Examples:

- `2.6.35.1` becomes `2.6.35.1`
- `2.6.35.0` becomes `2.6.35`
- `2.6.35` becomes `2.6.35`

### Client cookie

HoN client uses a 32 byte cookie that is passed around. In case you need it you can get it from the HoN client. It looks like `12345678a2b4c6d8e2f4162832445668`.

This is not a valid cookie.

Currently you can manually set it in `main.py` `main()` function, when calling `_client.patcher()`.

## HoN client information

HoN client is avaliable for the following platforms:

- Windows
- Linux
- MacOS
