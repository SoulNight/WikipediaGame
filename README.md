# WikipediaGame

This website is currently not deployed but there are instructions below of how to download, install and run it on your own machine.

## Installation

(these instructions should work under GNU/Linux and Macos)

Prerequisites: Python

```
git clone https://github.com/alexhkurz/WikipediaGame.git
cd WikipediaGame/server
source setup.sh
```

Starting the server:

```
python server.py
```

(For development one may want to use `watchmedo auto-restart -d . -p '*.py' -- python server.py`.)

Play the game on [`localhost:5000`](http://127.0.0.1:5000/) (this link will only work after you started the server on your machine).

## Branches

- `version1` computes the shortest path betwen two wikipedia pages
- `version2` (=`main`) additionally displays all pages visited during the computation
- `dev` will output the pages being visited in real time (under development)


