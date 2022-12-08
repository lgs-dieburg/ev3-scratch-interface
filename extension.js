class ScratchFetch {

    constructor() {
    }

    getInfo() {
        return {
            "id": "ev3-scratch-interface",
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
                }
            ],
        };
    }

    url = "https://e13d-213-157-8-90.eu.ngrok.io/"

    forwards({timeout}){
        return fetch([this.url, "forwards?timeout=", timeout, "&speed=50"].join(""), {
            headers: new Headers({
                "ngrok-skip-browser-waring": "69"
            }),
        }).then(response => response.text())
    }

    backwards({timeout}){
        return fetch([this.url, "backwards?timeout=", timeout, "&speed=50"].join(""), {
            headers: new Headers({
                "ngrok-skip-browser-waring": "69"
            }),
        }).then(response => response.text())
    }

    turn({degrees}){
        return fetch([this.url, "turn?degrees=", degrees].join(""), {
            headers: new Headers({
                "ngrok-skip-browser-waring": "69"
            }),
        }).then(response => response.text())
    }
}

Scratch.extensions.register(new ScratchFetch())