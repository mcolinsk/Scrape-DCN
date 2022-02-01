# DCN Export and Download Data - Python Browser Automation with Selenium

---
## About

Automate downloading of information from DCN through the browser using selenium

## Setup

- edit the file config_template.py
  - enter the company name you want to search for
  - enter the location want to search for
  - note, you can leave the location blank
  - rename file to config.py

---
## Run Code
- to download DCN data[^1]
  > python3 Python_DCN.py

    [^1]:NOTE: python version must be 3.9. pandas is not yet supported for python 3.10
## Additional Flags
- run headless
  > -headless
  > or
  > -debug
- log terminal output to a file
  > -logoutput