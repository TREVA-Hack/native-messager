async function getEcho360DownloadLink(url) {
    // We assume we already have all the cookies necessary to access the page
    let url2 = new URL(url.slice(0, url.lastIndexOf('/')) + "/media");

    const response = await fetch(url2);

    if (!response.ok) {
        throw new Error("Response was not ok: " + response.status + " " + response.statusText); 
    }

    const data = await response.json();

    let files = data.data[0].video.media.media.current.audioFiles

    largest_audio_file = files.sort((a, b) => b.size - a.size)[0]

    return largest_audio_file.s3Url;
}

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
                console.log(srt);
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

function listenForClicks(current_tab_url) {
    document.addEventListener("click", (e) => {
        console.debug("something pressed");

        if (e.target.tagName !== "BUTTON" || !e.target.closest("#popup-content")) {
            // Ignore when click is not on a button within <div id="popup-content">
            return;
        }

        console.debug("button pressed");

        let video_link = getEcho360DownloadLink(current_tab_url);

        video_link.then((link) => {
            console.log("Downloading: " + link);

            downloadFile(link).then((path) => {
                console.log("Downloaded: " + path);
                document.getElementById("progress").textContent = `Downloaded: ${path}`;
                interactWithNativeApp(path);
            });
        });
    });
}

function reportExecuteScriptError(error) {
    document.getElementById("progress").textContent = `Download failed: ${error.message}`;
    console.error(`Download failed: ${error.message}`);
}

browser.tabs.query({active: true, currentWindow: true}).then((tabs) => {
    let current_tab_url = tabs[0].url;
    console.debug("We are at " + current_tab_url);
    let url = new URL(current_tab_url);
    if (url.hostname !== "echo360.org.uk") {
        document.querySelector("#popup-content").classList.add("hidden");
        document.querySelector('#not-on-echo360').classList.remove("hidden");
    } else if (url.pathname.indexOf("/lesson") !== 0) {
        document.querySelector("#popup-content").classList.add("hidden");
        document.querySelector('#lecture-not-open').classList.remove("hidden");
    } else {
        listenForClicks(current_tab_url).catch(reportExecuteScriptError);
    }
})
