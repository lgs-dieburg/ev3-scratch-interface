class ScratchFetch {
    url
    availableUnits = []

    constructor() {
        this.getAvailableUnits()
            .then(r => {
                this.availableUnits = r
                this.setURL({index: 0})
            })
    }

    async getInfo() {
        return {
            "id": "MilanTheissEv3ScratchInterface",
            "name": "EV3 Scratch Interface",
            "blocks": [
                {
                    "opcode": "forwards",
                    "blockType": "command",
                    "text": "Fahre vorwärts für [timeout] Sekunden",
                    "arguments": {
                        "timeout": {
                            "type": "number",
                            "defaultValue": 2
                        },
                    }
                },
                {
                    "opcode": "backwards",
                    "blockType": "command",
                    "text": "Fahre rückwärts für [timeout] Sekunden",
                    "arguments": {
                        "timeout": {
                            "type": "number",
                            "defaultValue": 2
                        },
                    }
                },
                {
                    "opcode": "turn",
                    "blockType": "command",
                    "text": "Dreh dich um [degrees] Grad",
                    "arguments": {
                        "degrees": {
                            "type": "number",
                            "defaultValue": 90
                        },
                    }
                },
                {
                    "opcode": "setURL",
                    "blockType": "command",
                    "text": "Führe auf dem [availableUnits] Grad",
                    "arguments": {
                        "unit": {
                            "type": "text",
                            "menu": "availableUnits"
                        }
                    },
                    "menus": {
                        "availableUnits": {
                            "items": (await this.getAvailableUnits()).map(val => val.name)
                        },
                    }
                }
            ],
        };
    }

    // INFO Fetch Requests mode: cors & new Header: ngrok-skip-browser-warning
    forwards({timeout}) {
        return fetch([this.url, "/forwards?timeout=", timeout, "&speed=50"].join(""), {
            mode: "cors",
            headers: new Headers({
                "ngrok-skip-browser-warning": "69420"
            })
        }).then(response => response.text())
    }

    backwards({timeout}) {
        return fetch([this.url, "/backwards?timeout=", timeout, "&speed=50"].join(""), {
            mode: "cors",
            headers: new Headers({
                "ngrok-skip-browser-warning": "69420"
            })
        }).then(response => response.text())
    }

    turn({degrees}) {
        return fetch([this.url, "/turn?degrees=", degrees].join(""), {
            mode: "cors",
            headers: new Headers({
                "ngrok-skip-browser-warning": "69420"
            })
        }).then(response => response.text())
    }

    setURL({unitName = undefined, index = 0}) {
        if (typeof unitName !== "undefined") {
            this.url = this.availableUnits.find(val => val.name === unitName).url
        } else {
            this.url = this.availableUnits[index].url
        }
    }

    async getAvailableUnits(){
        let res = await fetch(`https://allorigins.hexlet.app/raw?url=${encodeURIComponent('https://gist.githubusercontent.com/milantheiss/9364995837bbd94ed548857c5b9f7f70/raw/localtunnels.json')}&disableCache=true`)
        res = await res.text()
        res = JSON.parse(res)
        return res
    }
}

Scratch.extensions.register(new ScratchFetch())