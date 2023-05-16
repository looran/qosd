## qosd - OSD from python

`qosd` can display text on your Linux desktop screen:
* display simple line
* tail stdin
* transparency and style is configurable

# Usage

```
usage: qosd.py [-h] [-i] [-m MAXLINES] [-n SESSION_NAME] [-o OPACITY] [-p {topleft,topright,bottomleft,bottomright}] [-P POSITION_OFFSET POSITION_OFFSET] [-s STYLE] [-t TIMEOUT] text [text ...]

qosd - OSD from python - v20230516

positional arguments:
  text                  text to display, or '-' for stdin

options:
  -h, --help            show this help message and exit
  -i, --no-input        set window transparent to input
  -m MAXLINES, --maxlines MAXLINES
                        default: 20
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
                        display timeout in seconds, default: 2.5

examples:
$ qosd hello
$ tail -f /var/log/{messages,auth.log} | qosd -
```
