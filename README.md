# About

MOBIB-extractor allows you to read the data stored on your STIB Mobib card.

# License

(c) 2009 MOBIB Extractor project. This software is provided 'as-is',
without any express or implied warranty. In no event will the authors be held
liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to no restriction.

Technical remarks and questions can be addressed to
<tania.martin@uclouvain.be>
<jean-pierre.Szikora@uclouvain.be>

# Installation

## on Linux

You must install:
- pcsc_lite
- ccid
- python
- the python library PIL 
- pyscard

If you use the smartcard reader ACS ACR38, you have to install the
corresponding package.


## on Mac OS X 10.5.6 (last version)

As this new version contains pcsc_lite, ccid and python, you only have to
install:
- the python library PIL
- pyscard (the mpkg is easily found on the web)
If you use the smartcard reader ACS ACR38, the driver mpkg can be found on the
manufacturer (ACS) website.


## on Windows

You must install:
- python
- the python library PIL
- pyscard
If you use the smartcard reader ACS ACR38, the driver can be found on the
manufacturer (ACS) website.

# Run

You can then launch the application MOBIB-Extractor.py in the terminal using
the command:
- For UNIX architecture : ./MOBIB-Extractor.py or python MOBIB-Extractor.py
- For Windows : MOBIB-Extractor.py

# User manual

1- If you want to read a card:
1.1- Plug your reader and put your card on
1.2- Click File and click Acquisition
2- If you want to read an old dump file card:
2.1- Click File and click Open dump
2.2- Then select the file you want to read
3- If you want to save a dump card:
3.1- Click File and click Save dump
3.2- Then choose the name and directory to record the dump

# Keyboard shortcuts

- <Double-Click> to zoom + or -
- <MouseWheel> to vertical scroll
- <Left arrow> to scroll left
- <Right arrow> to scroll right
- <Up arrow> to scroll up
- <Down arrow> to scroll down
- <Esc> to leave the program
- <a> to dump a card
- <o> to open a dump
- <s> to save a dump
