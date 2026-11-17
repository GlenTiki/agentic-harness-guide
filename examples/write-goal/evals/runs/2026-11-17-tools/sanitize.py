import getpass
import json
import re
import sys

# The init event lists local machine details (memory and scratch folders, sockets, installed skills).
# Keep only the fields that describe the run, and replace any temporary folder path that is left.
# The commands list names installed skills and connected accounts. Rate limit events and usage, cost, credit and request id fields describe the account, not the run: drop them.
KEEP = ('type', 'subtype', 'cwd', 'tools', 'model', 'permissionMode', 'claude_code_version')
DROP_EVENTS = {'rate_limit_event'}
DROP_FIELDS = {'total_cost_usd', 'request_id', 'usage', 'modelUsage', 'model_usage_since_last_result',
               'credential_expires_at', 'fast_mode_state', 'fast_mode_disabled_reason', 'rate_limit_info'}
TEMP_PATH = re.compile(r'/(private/)?tmp/[^"\s\\]*')
USER_NAME = re.compile(r'(?<= )' + re.escape(getpass.getuser()) + r'(?=  )')


def strip(value):
    if isinstance(value, dict):
        return {k: strip(v) for k, v in value.items() if k not in DROP_FIELDS}
    if isinstance(value, list):
        return [strip(v) for v in value]
    return value


for path in sys.argv[1:]:
    lines = []
    for line in open(path):
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get('type') in DROP_EVENTS or event.get('subtype') == 'commands_changed':
            continue
        if event.get('type') == 'system' and event.get('subtype') == 'init':
            event = {key: event[key] for key in KEEP if key in event}
        lines.append(USER_NAME.sub('<user>', TEMP_PATH.sub('<tmp>', json.dumps(strip(event)))))
    open(path, 'w').write('\n'.join(lines) + '\n')
