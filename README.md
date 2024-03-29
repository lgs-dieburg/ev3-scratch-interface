[![Extentsion](https://github.com/milantheiss/ev3-scratch-interface/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/milantheiss/ev3-scratch-interface/actions/workflows/pages/pages-build-deployment)

# Interface zwischen ev3dev und Scratch
Mit diesem Interface lässt sich der Lego Mindstorm EV3 Roboter mit Scratch steuern, auch wenn eine Firewall oder Software einer direkten Kommunikation im Weg stehen.

Das Interface wurde für den Tag des offenen Unterrichts an der [Landrat-Gruber-Schule Dieburg](https://lgs-dieburg.de) entwickelt.  
Das Interface nutzt einen gemoddeten Scratch Client, um mit einer Scratch Extension auf REST Endpoint zuzugreifen.  
Die Requests werden dann vom API Host interpretiert und an den EV3 geschickt.

## Setup

#### EV3
- Verbinde den EV3 über das gleiche Netzwerk mit dem Host Computer.
  - Am einfachsten ist es, den EV3 mit dem Hotspot des Host Computer zu verbinden.  
  - Wenn der EV3 keine Verbindung findet, kontrolliere mit wie viel GHz des Wifi arbeitet.  
  Wahrscheinlich wird für eine 2.4 GHz Wifi Verbindung benötigt. 
- Definiere die IP-Adresse des EV3 Roboters in settings.json
- Starte ev3_control.py

#### Host Computer
- Definiere die IP-Adresse des EV3 Roboters in settings.json
- Starte control.py
  - Die REST API startet standardmäßig auf http://localhost:5000
- Öffne einen Localtunnle mit [ngrok](https://ngrok.com) Port 5000 - `ngrok http 5000`
- Übertrage die URL in dein Gist, damit die URL von extension.js ausgelesen werden kann.
  - Achtung: allorigins.hexlet.app cacht Request für ca. 2 Minuten. Warte also nach einer Änderung der URL mehr als 2 Minuten, wenn in den letzten 2 Minuten vor einer Änderung von der Extension auf allorignis.hexlet.app zugegriffen wurde. 

#### Schüler Computer
- Launch gemoddeten [Scratch Client mit Extension](https://sheeptester.github.io/scratch-gui/?url=https://lgs-dieburg.github.io/ev3-scratch-interface/extension.js). (Über diesen Link sollte alles automatisch geladen werden.)
- Wenn Scratch nicht die URL zum Localtunnel aufrufen kann, versuche die URL einmal im Browser aufzurufen.
- Die Befehle werden an den Host Computer gesendet, sobald ein Block ausgeführt wird 

## Adaption für andere Zwecke  
Das Interface kann auch außerhalb von Scratch genutzt werden, so lang auf die API Endpunkte aufgerufen werden können. 

## Erweiterung zum neue Befehle  
Um neue, vom EV3 Roboter interpretierbare Befehle hinzuzufügen, müssen ```host/control.py``` & ```ev3/control.py``` modifiziert werden.  
In host/control.py muss ein neuer API Endpoint hinzugefügt werden. Eine neue Methode muss mit ```@app.route("/<Befehl>")``` & ```@cross_origin()``` beschrieben sein, damit Flask die Methode bei einem API Call an die angegebene Adresse aufruft. 
[Mehr Infos zu Flask hier](https://flask.palletsprojects.com/en/2.2.x/)  
In der neuen Methode kann mit ```controller.add_request_to_queue()``` ein neue Request an den EV3 gesendet werden. ```add_request_to_queue``` verlangt zwei Parameter.
Zuerst wird die Send Methode verlangt und dann in einem dict Argumente.

Requests an den EV3 werden in ```ev3/control.py```: ```process_request``` verarbeitet. Der neue Command muss zum IF-Statement hinzugefügt werden und mit der Aktion, die der EV3 ausführen soll verbunden werden.
