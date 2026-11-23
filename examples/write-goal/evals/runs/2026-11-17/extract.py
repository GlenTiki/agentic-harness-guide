import re
import sys

text = open(sys.argv[1]).read()
section = text.split('## Input', 1)[1].split('\n## ', 1)[0]
blocks = re.findall(r'^(`{3,})text\n(.*?)\n\1$', section, re.S | re.M)
print('\n\n'.join(body for _, body in blocks), end='')
