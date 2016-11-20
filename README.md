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

### Install from source
```
git clone https://github.com/di-unipi-socc/tosKer/tree/master
cd tosca-parser
sudo python setup.py install
```

use command:
```
tosker tosker/test/TOSCA/wordpress.yaml create start
```

run the tests:
```
python setup.py test
```
