# Backend

Run `pip install -r requirements.txt`, create `backend/uploads` if it doesn't already exist, and then `python3 TREVA/backend/main.py`.

Upload the `.srt` file with a POST request to `http://localhost:8000/upload`, the returned JSON will contain the result under the field `message`.

# Browser extension

Currently, I have no idea how to get this working on Windows or Mac.

For Linux, specifically Ubuntu 22.04-based distributions, to run on Firefox:

(please _do_ be alarmed by the overuse of `sudo` and make sure to read all the source code because even I do not trust it)

```bash
sudo cp RunWhisper.json /usr/lib/mozilla/native-messaging-hosts/RunWhisper.json
sudo cp functionality.py /usr/bin/functionality.py
sudo chmod +x /usr/bin/functionality.py
```

Then open the `about:debugging` webpage in Firefox -> This Firefox -> Temporary Extensions -> Load Temporary Add-on -> select `manifest.json`

In Temporary Extensions, you can also press Inspect to see the developer console for the addon. Run it before opening the addon popup window.

`popup.js` will download a video and convert it to an SRT file: this SRT file will be dumped in the console logs.
