import requests
import json
input = '周期信号频谱的三个性质是什么？'
params = {'input': input}
rl = requests.get('http://58.199.162.205:34510/QA/all', params=params)
info = json.loads(rl.text)
print(input,end='\n\n')
print(info['output'])