class ScratchFetch {
    constructor() {
    }

    getInfo() {
        return {
            "id": "ev3-scratch-interface",
            "name": "EV3 Scratch Interface",
            "blocks": [
                {
                    "opcode": "fetchURL",
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
                    "opcode": "fetchURL",
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
                    "opcode": "fetchURL",
                    "blockType": "command",
                    "text": "Dreh dich um [degrees] Grad",
                    "arguments": {
                        "degrees": {
                            "type": "number",
                            "defaultValue": 2
                        },
                    }
                }
            ],
        };
    }

    fetchURL({ url }) {
        return fetch(url, {
            headers: new Headers({
                "ngrok-skip-browser-waring": "69"
            }),
        }).then(response => response.text())
    }
}

Scratch.extensions.register(new ScratchFetch())