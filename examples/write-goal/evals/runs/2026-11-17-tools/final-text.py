import json
import sys

result = None
for line in open(sys.argv[1]):
    line = line.strip()
    if not line:
        continue
    event = json.loads(line)
    if event.get('type') == 'result':
        result = event.get('result')
print(result if result is not None else '[no result event in the transcript]')
