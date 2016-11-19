# tosKer
[Slides](http://slideck.io/gist.github.com/lucarin91/d2e834106a4d0f72b4f369d4d5e46bfa/tosker-slide.md)

## Intallation
**Requirements**
- python>=2.7
- pip

```
pip install tosker
```
```
tosker <TOSCA-file> <operations> <inputs>
```

example:
```
tosker tosker/test/TOSCA/wordpress.yaml create start
tosker tosker/test/TOSCA/wordpress.yaml stop delete
```

### Install by source
```
git clone https://github.com/lucarin91/tosKer

virtualenv venv -p python3

. ./venv/bin/activate

pip install -r requirements.txt
```

use command:
```
./tosKer tosker/test/TOSCA/wordpress.yaml create start
```

run the tests:
```
python -m unittest discover
```
