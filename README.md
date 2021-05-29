# FlagsMashupBot

Live demo:
http://flagsmashupbot.pythonanywhere.com/



![alt text](https://i.imgur.com/LSepqer.png)

https://twitter.com/FlagsMashupBot
-------------------------------------------------------

## Prerequisites
 - Python3
 - Pycairo's [required files in your machine](https://pycairo.readthedocs.io/en/latest/getting_started.html)

### Clone the repo
```bash
git clone https://github.com/antooro/FlagsMashupBot
````

### Start a virtual environment
**LINUX/OSX**: Inside the repo folder
```bash
python -m ./ # starts the venv in the current folder
source bin/activate # On LINUX or OSX
.\Scripts\activate # ONLY Windows
```

To exit the Virtual Environment on any OS
```bash
deactivate
```

### Install the requirements:
```bash
pip install -r requirements.txt
```

Try the image generator 

```bash
python formatsvg.py
```

It will generate 3 files: the 2 country flags, and the mashup flag
