import whisper

# import json
# import struct
# from concurrent.futures import ThreadPoolExecutor
import nativemessaging
import pydub


model = whisper.load_model("tiny")


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


def transcribe_in_chunks(audio_path, chunk_size_seconds=30):
    """Transcribe an audio file in chunks and yield partial transcriptions.

    Args:
        audio_path (str): Path to the audio file.
        chunk_size_seconds (int): Desired length of each chunk in seconds. Defaults to 30.
    """

    audio = pydub.AudioSegment.from_file(audio_path)

    # Calculate chunk duration in milliseconds
    chunk_size_ms = chunk_size_seconds * 1000

    # Split into chunks
    for start in range(0, len(audio), chunk_size_ms):
        end = min(start + chunk_size_ms, len(audio))
        chunk = audio[start:end]

        # Save the chunk temporarily (Arjav says to note that this creates temp files)
        temp_chunk_path = f"chunk_{start}.wav"
        chunk.export(temp_chunk_path, format="wav")

        result = model.transcribe(temp_chunk_path)
        yield result["text"]


# def async_transcribe_and_send(audio_path):
#     """Asynchronously transcribe audio and send the transcription."""
#     with ThreadPoolExecutor(max_workers=1) as executor:
#         future = executor.submit(transcribe, audio_path)
#         while not future.done():
#             pass
#         transcription = future.result()
#         response = {"transcription_fragment": transcription, "done": True}
#         send_message(response)


def main():
    while True:
        message = nativemessaging.get_message()
        if "audio_path" in message:
            for transcription_fragment in transcribe_in_chunks(message["audio_path"]):
                response = {
                    "transcription_fragment": transcription_fragment,
                    "done": False,
                }
                nativemessaging.send_message(response)
            # Send final "done": True message after complete transcription
            nativemessaging.send_message({"transcription_fragment": "", "done": True})
        else:
            nativemessaging.send_message(
                {"error": "No audio_path provided", "done": True}
            )


if __name__ == "__main__":
    main()
