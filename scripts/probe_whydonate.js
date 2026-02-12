const WebSocket = require('ws');
const axios = require('axios');

async function probe() {
    const CDP_URL = "http://127.0.0.1:9222/json";
    console.log(`Checking CDP: ${CDP_URL}`);

    try {
        const resp = await axios.get(CDP_URL);
        const tabs = resp.data;
        console.log(`Found ${tabs.length} tabs.`);

        const target = tabs.find(t => t.url.includes('whydonate.com') && t.type === 'page');
        if (!target) {
            console.log("No WhyDonate tab found.");
            return;
        }

        console.log(`Connecting to: ${target.webSocketDebuggerUrl}`);
        const ws = new WebSocket(target.webSocketDebuggerUrl, {
            headers: {
                "Host": "127.0.0.1:9222",
                "Origin": "http://127.0.0.1:9222"
            }
        });

        ws.on('open', () => {
            console.log("WebSocket Connected!");

            // Send evaluate
            const msg = {
                id: 1,
                method: "Runtime.evaluate",
                params: {
                    expression: "({ url: window.location.href, text: document.body.innerText.substring(0, 100) })",
                    returnByValue: true
                }
            };
            ws.send(json.stringify(msg));
        });

        ws.on('message', (data) => {
            console.log(`Received: ${data}`);
            ws.close();
        });

        ws.on('error', (err) => {
            console.error(`WS Error: ${err.message}`);
        });

    } catch (e) {
        console.error(`Error: ${e.message}`);
    }
}

probe();
