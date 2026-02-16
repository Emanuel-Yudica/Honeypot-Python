import json
import time
from .tasks import process_event


def watch_multiple(files):

    positions = {file: 0 for file in files}

    while True:
        for file in files:

            with open(file, "r") as f:

                f.seek(positions[file])

                line = f.readline()

                while line:

                    event = json.loads(line)

                    process_event.delay(event)

                    line = f.readline()

                positions[file] = f.tell()

        time.sleep(0.1)

