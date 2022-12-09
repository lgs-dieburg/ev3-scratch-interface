class ScratchFetch {
    url

    constructor() {
        fetch(`https://api.allorigins.win/get?url=${encodeURIComponent('https://gist.githubusercontent.com/milantheiss/aebe6ff4e1afaa380688319b28072616/raw/21586fb5a2d78be8c27ecb380fb30e595b6ee00d/localtunnel_ev3_scratch_interface')}`)
            .then(res => res.text())
            .then(res => JSON.parse(res))
            .then(res => this.url = res.contents)
    }

    getInfo() {
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
                }
            ],
        };
    }

    forwards({timeout}) {
        return fetch([this.url, "/forwards?timeout=", timeout, "&speed=50"].join(""), {
            headers: new Headers({
                "ngrok-skip-browser-warning": "69420"
            })
        }).then(response => response.text())
    }

    backwards({timeout}) {
        return fetch([this.url, "/backwards?timeout=", timeout, "&speed=50"].join(""), {
            headers: new Headers({
                "ngrok-skip-browser-warning": "69420"
            })
        }).then(response => response.text())
    }

    turn({degrees}) {
        return fetch([this.url, "/turn?degrees=", degrees].join(""), {
            headers: new Headers({
                "ngrok-skip-browser-warning": "69420"
            })
        }).then(response => response.text())
    }
}

Scratch.extensions.register(new ScratchFetch())