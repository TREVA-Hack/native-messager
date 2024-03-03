#!/usr/bin/python3

import nativemessaging

nativemessaging.send_message("Script started")

import traceback

import sys

print("Script started\n", file=sys.stderr)

sys.stderr.write("Script started\n")

import whisper

sys.stderr.write("Whisper imported\n")

import json
# import struct
# from concurrent.futures import ThreadPoolExecutor
import pydub

sys.stderr.write("All imported\n")

# def send_message(message):
#     """Send a JSON message to the browser extension."""
#     encoded_message = json.dumps(message).encode("utf-8")
#     # Struct makes sure the message length is sent in  platform-agnostic (independent) way
#     sys.stdout.buffer.write(struct.pack("I", len(encoded_message)))
#     sys.stdout.buffer.write(encoded_message)
#     sys.stdout.flush()


# def receive_message():
#     """Receive a JSON message from the browser extension."""
#     raw_length = sys.stdin.buffer.read(4)
#     if not raw_length:
#         sys.exit(0)
#     message_length = struct.unpack("I", raw_length)[0]
#     message = sys.stdin.buffer.read(message_length).decode("utf-8")
#     return json.loads(message)


# def transcribe(audio_path):
#     """Transcribe the audio file."""
#     result = model.transcribe(audio_path)
#     return result["text"]


# def transcribe_in_chunks(audio_path, chunk_size_seconds=30):
#     """Transcribe an audio file in chunks and yield partial transcriptions.

#     Args:
#         audio_path (str): Path to the audio file.
#         chunk_size_seconds (int): Desired length of each chunk in seconds. Defaults to 30.
#     """

#     audio = pydub.AudioSegment.from_file(audio_path)

#     # Calculate chunk duration in milliseconds
#     chunk_size_ms = chunk_size_seconds * 1000

#     # Split into chunks
#     for start in range(0, len(audio), chunk_size_ms):
#         end = min(start + chunk_size_ms, len(audio))
#         chunk = audio[start:end]
#         result = model.transcribe(chunk)
#         yield result["text"]


# def async_transcribe_and_send(audio_path):
#     """Asynchronously transcribe audio and send the transcription."""
#     with ThreadPoolExecutor(max_workers=1) as executor:
#         future = executor.submit(transcribe, audio_path)
#         while not future.done():
#             pass
#         transcription = future.result()
#         response = {"transcription_fragment": transcription, "done": True}
#         send_message(response)


def secsToHoursMinsSecsMillis(i):
    hours = i // 3600
    mins = (i - hours*3600) // 60
    secs = (i - hours*3600 - mins*60) // 1
    millis = ((i - hours*3600 - mins*60 - secs) * 1000) // 1
    return (hours, max(0,mins), max(0,secs), max(0,millis))


def toTimestamp(h, m, s, ml):
    result = ""

    def pad0(x):
        nonlocal result
        if x > 9:
            result += str(x)
        else:
            result += "0" + str(x)

    pad0(int(h))
    result += ":"
    pad0(int(m))
    result += ":"
    pad0(int(s))
    result += ","

    ml1 = int(ml)
    if ml1 > 99:
        result += str(ml1)
    elif ml1 > 9:
        result += "0" + str(ml1)
    else:
        result += "00" + str(ml1)

    return result


def toSRT(segments) -> str:
    result = ""

    for i, seg in enumerate(segments):
        result += str(i) + "\n"
        (h1, m1, s1, ml1) = secsToHoursMinsSecsMillis(seg['start'])
        t1 = toTimestamp(h1, m1, s1, ml1)
        (h2, m2, s2, ml2) = secsToHoursMinsSecsMillis(seg['end'])
        t2 = toTimestamp(h2, m2, s2, ml2)
        result += t1 + " --> " + t2 + "\n"
        result += seg['text'] + "\n" + "\n"

    return result


def main():
    nativemessaging.send_message("MAIN STARTED")

    sys.stderr.write("Main started\n")

    model = whisper.load_model("tiny")

    sys.stderr.write("Whisper model initialised\n")

    while True:
        message = nativemessaging.get_message_raw()  # Receive message from the extension
        nativemessaging.send_message(message)
        nativemessaging.send_message("Debug statement 0")
        if "audio_path" in message:
            audio_path = json.loads(message)["audio_path"]  # Extract the audio path

            result = model.transcribe(audio_path)
            transcription = result["segments"]
            response = {"transcription": toSRT(transcription), "done": True}

            nativemessaging.send_message(json.dumps(response))
            break

        else:
            error_response = {"error": "No audio_path provided", "done": True}
            nativemessaging.send_message(json.dumps(error_response))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        nativemessaging.send_message(str(e))
        nativemessaging.send_message(traceback.format_exc())
        exit(1)
