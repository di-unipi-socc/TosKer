# tosKer

---

## Feature
- descrizione del deployment attraverso un subset di TOSCA yaml
- supporta il deployment di docker container e docker volumes
- supporta il deployment di componenti software generici attraverso il TOSCA lifecycle
- permette la connessione delle varie componenti in rete

---

## TOSCA
- supporta solo 3 tipi custom per i componenti (no tipi normative, ne tipi derivati)
- supporta le gli input e gli output di TOSCA
- supporta le funzioni (get_inputs, get_attribute, get_property)
- supporta lo Standard lifecycle (per il tipo software)
- supporta il sistema di requirements tra i componenti di TOSCA

---

### Custom Types
Esistono tre tipi custom type supportati:

- `tosker.docker.container` rappresenta un container di docker con tutte le proprietà adatte per la sua creazione, il suo lifecicle è quello implicito in docker
- `tosker.docker.volume` rappresentano un volume di dokcer con le varie proprietà
- `tocker.software` rappresenta un nodo generico software gestito con lo Standard lifecycle di TOSCA

---

### Requirements
- è possibile hostare un tipo software sopra un altro tipo software o un container  
- è possibile connettere due container, due software o software e container
- i volumi possono solo essere connessi a container

---

## Deployment di TOSCA
le operazioni possibili da eseguire su un file TOSCA sono:

- **create**, crea tutti i componenti dell'applicazione
- **start**, lancia tutti i componenti dell'applicazione se esistono
- **stop**, ferma l'esecuzione di tutti i componenti dell'applicazione
- **delete**, rimuove tutti i componenti dell'applicazione se esistono

___

Tutte le operazione presuppongono uno stato pregresso dell'applicazione.

Per esempio l'operazione di start può essere eseguita se precedentementi tutti i componenti sono stati creati

___

Il deployment dei componenti software è eseguto aggiungendo layer sull'immagine di docker.

Gli scprit per implementare le operazioni vengono eseguito con un'operazione di start o exec sul container.

---

## Implementazione
Compatibile con python >=2.7, OS linux

librerie usate:

- tosca-parser (openstack)
- py-docker

---

## Commando doc
La libreria è disponibile sulla repository PyPi ed è possibilie scaricare con `pip intall tosker`

La sintassi del programma è la seguete
```
tosker <TOSCA file> <operations> <inputs>
```

- `TOSCA file`, nome del file tosca o della cartella in cui è contenuto
- `operations`, lista di operazioni da eseguire sul file TOSCA (create, start, stop, delete)
- `inputs`, lista di parametri da dare in input al file TOSCA

___

example:
```
tosker hello.yaml create --name mario

tosker hello.yaml start --name mario

tosker hello.yaml stop --name mario

tosker hello.yaml delete --name mario

tosker hello.yaml create start --name mario

tosker hello.yaml stop delete --name mario

```

---

## Tests
Sono attualmente disponibili 12 test:

- hello            
- dockerfile       
- wordpress
- wordpress_theme
- wordpress_volume
- wordpress_ligth     
- software_link       

___

- software_lifecycle  
- node_mongo_mix2           
- node_mongo_mix1  
- node_mongo                
- node_mongo_single_server  
