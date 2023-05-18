## qosd - display text over your Xorg screen

`qosd` is a command-line tool and python library can display text over your Linux desktop screen:
* text is displayed over any window (On-Screen-Display)
* display simple line
* tail stdin
* transparency and text style is configurable

# Install

```
pip install qosd
```

# Usage

```
usage: qosd [-h] [-i] [-m MAXLINES] [-n SESSION_NAME] [-o OPACITY] [-p {topleft,topright,bottomleft,bottomright}] [-P POSITION_OFFSET POSITION_OFFSET] [-s STYLE] [-t TIMEOUT] text [text ...]

qosd - OSD from python - v20230516

positional arguments:
  text                  text to display, or '-' for stdin

options:
  -h, --help            show this help message and exit
  -i, --no-input        set window transparent to input
  -m MAXLINES, --maxlines MAXLINES
                        default: 30
  -n SESSION_NAME, --session-name SESSION_NAME
                        start named OSD display session, killing previous OSD with same session name
  -o OPACITY, --opacity OPACITY
                        default: 1.0
  -p {topleft,topright,bottomleft,bottomright}, --position {topleft,topright,bottomleft,bottomright}
                        text position, default=topleft
  -P POSITION_OFFSET POSITION_OFFSET, --position-offset POSITION_OFFSET POSITION_OFFSET
                        offset in pixels from position, default: 0 0
  -s STYLE, --style STYLE
                        default: 'color:"#FFFFFF";background-color:"#99000000";font-size:11pt;font-weight:bold;'
  -t TIMEOUT, --timeout TIMEOUT
                        display timeout in seconds, default: 3

examples:
$ qosd hello
$ tail -f /var/log/{messages,auth.log} | qosd -
```
