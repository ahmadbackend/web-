import json
import aiofiles
from dotenv import load_dotenv
from django.conf import settings
load_dotenv()
from channels.generic.websocket import AsyncWebsocketConsumer

class FileRead(AsyncWebsocketConsumer):
    async def connect(self):
        self.file_path =settings.FILE_PATH
        self.file_position = 0  # Track the last read position
        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")

        chunk = await self.read_next_chunk()  # Read only 100 lines

        await self.send(text_data=json.dumps({"chunk": chunk}))

    async def read_next_chunk(self, chunk_size=100):
        """ Read the next 100 lines from the file based on the last position. """
        chunk = []
        async with aiofiles.open(self.file_path, 'r') as file:
            await file.seek(self.file_position)  # Move to last read position

            for _ in range(chunk_size):
                line = await file.readline()
                if not line:  # Stop if EOF reached
                    break
                chunk.append(line.strip())  # Store line without newline character

            self.file_position = await file.tell()  # Save the new position

        return chunk
