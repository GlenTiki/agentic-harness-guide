import re
import sys

# The message is the text block under "## Input" in the eval file.
section = open(sys.argv[1]).read().split('## Input', 1)[1].split('\n## ', 1)[0]
print(re.search(r'^```text\n(.*?)\n```$', section, re.S | re.M).group(1), end='')
