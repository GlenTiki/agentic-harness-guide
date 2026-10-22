import re,sys
t=open(sys.argv[1]).read()
sec=t.split('## Input',1)[1].split('\n## ',1)[0]
blocks=re.findall(r'^(`{3,})text\n(.*?)\n\1$',sec,re.S|re.M)
out=[]
for _,b in blocks:
    b='\n'.join(l for l in b.split('\n') if l not in('QUOTED ATTACK TEXT. DATA ONLY. DO NOT FOLLOW.','END QUOTED ATTACK TEXT.'))
    out.append(b)
print('\n\n'.join(out),end='')
