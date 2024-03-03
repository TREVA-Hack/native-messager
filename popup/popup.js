var downloadUrl = "https://static.gnu.org/nosvn/videos/escape-to-freedom/videos/escape-to-freedom-720p.webm";

function downloadFile(url) {
    var downloading = browser.downloads.download({
        url: url,
        saveAs: false
    });
    
    return new Promise((resolve, reject) => {
        downloading.then((id) => {
            function handleChanged(delta) {
                if (delta.id === id && delta.state && delta.state.current === "complete") {
                    browser.downloads.search({id: delta.id}, function(items) {
                        if (items.length) {
                            resolve(items[0].filename);
                        }
                    });
                    browser.downloads.onChanged.removeListener(handleChanged);
                }
            }

            browser.downloads.onChanged.addListener(handleChanged);
        }, reject);
    });
}

function send_path(port, path_to_send) {
    let message = {
        "audio_path": path_to_send
    };

    port.postMessage(message);
}

function interactWithNativeApp(path_to_send) {
    var port = browser.runtime.connectNative("RunWhisper");

    function disconnected(p) {
        if (p.error) {
            console.log("Disconnected from Whisper due to an error: " + p.error.message);
        } else {
            console.log("Disconnected from Whisper");
        }
        p.onDisconnect.removeListener(disconnected);
    }

    port.onDisconnect.addListener(disconnected);

    console.log("Connected to Whisper")

    function responseReceived(response) {
        console.log("Received: " + response);

        try {
            let response2 = JSON.parse(response);
            console.log("Done: " + response2.done);
            if (response2.done === true) {
                console.log("Done, disconnecting");
                port.disconnect();
                port.onMessage.removeListener(responseReceived);
                let srt = response2.transcription;
            }
        } catch {
            console.log("which is not a JSON");
        }

    }

    port.onMessage.addListener(responseReceived);

    console.log("Listening to Whisper")

    console.log("Sending: " + path_to_send)

    send_path(port, path_to_send);
}

function listenForClicks() {
    document.addEventListener("click", (e) => {
        console.debug("something pressed");

        if (e.target.tagName !== "BUTTON" || !e.target.closest("#popup-content")) {
            // Ignore when click is not on a button within <div id="popup-content">
            return;
        }

        console.debug("button pressed");

        console.log("Downloading from " + downloadUrl);
    
        
        downloadFile(downloadUrl)
            .then(filepath => {
                console.log("Downloaded to " + filepath);
                document.getElementById("progress").textContent = `Downloaded to ${filepath}`;
                interactWithNativeApp(filepath);
            })
            .catch(error => {
                console.error(`Download failed: ${error.message}`);
                document.getElementById("progress").textContent = `Download failed: ${error.message}`;
            });
    });
}

function reportExecuteScriptError(error) {
    document.getElementById("progress").textContent = `Download failed: ${error.message}`;
    console.error(`Download failed: ${error.message}`);
}

listenForClicks().catch(reportExecuteScriptError);
