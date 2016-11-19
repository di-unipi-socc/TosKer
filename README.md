# tosKer
[Slides](http://slideck.io/github.com/di-unipi-socc/tosKer/doc/slide.md)

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
