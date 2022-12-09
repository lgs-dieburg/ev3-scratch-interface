# Interface zwischen ev3dev und Scratch
Mit diesem Interface lässt sich der Lego Mindstorm EV3 Roboter mit Scratch steuern, auch wenn eine Firewall oder Software einer direkten Kommunikation im Weg stehen.

Das Interface wurde für den Tag des offenen Unterrichts an der [Landrat-Gruber-Schule Dieburg](https://lgs-dieburg.de) entwickelt.  
Das Interface nutzt einen gemoddeten Scratch Client, um mit einer Scratch Extension auf REST Endpoint zuzugreifen.  
Die Requests werden dann vom API Host interpretiert und an den EV3 geschickt.

## Setup

#### EV3
- Verbinde den EV3 in das gleiche Netzwerk, mit dem auch der Host Computer verbunden ist.
  - Am einfachsten ist es, den EV3 mit dem Hotspot des Host Computer zu verbinden.    
- Definiere die IP-Adresse des EV3 Roboters in settings.json
- Starte ev3_control.py

#### Host Computer
- Definiere die IP-Adresse des EV3 Roboters in settings.json
- Starte control.py
  - Die REST API startet standardmäßig auf http://localhost:5000
- Öffne einen Localtunnle mit [ngrok](https://ngrok.com) Port 5000 - `ngrok http 5000`
- Übertrage die URL in extension.js
  - Wenn extension.js committed wird, startet eine [Github Action](https://github.com/milantheiss/ev3-scratch-interface/actions/workflows/pages/pages-build-deployment) und pusht die Changes auf Github Pages
  - Sobald die Action abgeschlossen ist, kann der Schüler PC aufgesetzt werden.

#### Schüler Computer
- Die URL zum Localtunnel muss einmal im Browser aufgerufen werden und bestätigt werden, damit der Warning Bypass Cookie gespeichert wird.
- Launch gemoddeten [Scratch Client mit Extension](https://sheeptester.github.io/scratch-gui/?url=https://milantheiss.github.io/ev3-scratch-interface/extension.js). (Über diesen Link sollte alles automatisch geladen werden.)
- Die Befehle werden an den Host Computer gesendet, sobald ein Block ausgeführt wird 