## qosd - OSD from python

`qosd` can display text on your Linux desktop screen:
* display simple line
* tail stdin
* transparency and style is configurable

# Usage

```
usage: qosd.py [-h] [-m MAXLINES] [-n SESSION_NAME] [-o OPACITY] [-s STYLE] [-t TIMEOUT] text [text ...]

OSD from python - v20230510

positional arguments:
  text                  text to display, or '-' for stdin

options:
  -h, --help            show this help message and exit
  -m MAXLINES, --maxlines MAXLINES
                        default: 20
  -n SESSION_NAME, --session-name SESSION_NAME
                        start named OSD display session, killing previous OSD with same session name
  -o OPACITY, --opacity OPACITY
                        default: 1.0
  -s STYLE, --style STYLE
                        default: 'color:"#FFFFFF";background-color:"#99000000";font-size:11pt;font-weight:bold;'
  -t TIMEOUT, --timeout TIMEOUT
                        display timeout in stdin mode, default: 2.5

examples:
qosd hello
tail -f /var/log/{messages,auth.log} | qosd -
```
