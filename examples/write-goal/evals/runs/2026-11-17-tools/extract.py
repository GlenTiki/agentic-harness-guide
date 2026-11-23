import re
import sys

# The tools runs read the real fixture repository, so the pasted repository state is dropped,
# and so is the base commit in eval 5, which a fixture cannot reproduce.
text = open(sys.argv[1]).read()
section = text.split('## Input', 1)[1].split('\n## ', 1)[0]
blocks = re.findall(r'^(`{3,})text\n(.*?)\n\1$', section, re.S | re.M)
body = '\n\n'.join(b for _, b in blocks)
body = body.split('\n\nRepository state, pasted for you:', 1)[0]
body = body.replace(', base commit 8aa31d0', '')
print(body, end='')
