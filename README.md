**Requirements**
  - python>=3.2
  - pip

**Installation:**
```
pip install -r requirements.txt
```

**Execution**
```
./tosKer <TOSCA-file-name> <operations>
```
example:
```
./tosKer test/TOSCA/wordpress.yaml create start
./tosKer test/TOSCA/wordpress.yaml stop delete
```

run the tests:
```
python -m unittest
```
