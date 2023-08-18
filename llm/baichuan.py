import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.generation.utils import GenerationConfig
from flask import Flask,jsonify,request,session
from flask import render_template,make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY']=os.urandom(24)

tokenizer = AutoTokenizer.from_pretrained("baichuan-inc/Baichuan-13B-Chat", trust_remote_code=True, cache_dir = '/data/lmj/LLM/download')
model = AutoModelForCausalLM.from_pretrained("baichuan-inc/Baichuan-13B-Chat", torch_dtype=torch.float16, trust_remote_code=True, cache_dir = '/data/lmj/LLM/download')
model = model.quantize(8).cuda() 
model.generation_config = GenerationConfig.from_pretrained("baichuan-inc/Baichuan-13B-Chat", cache_dir = '/data/lmj/LLM/download')
@app.route('/chat',methods=['GET','POST'])
def chat():
    if request.method == 'GET':
        _input = str(request.args.get('input'))
        messages = []
        messages.append({"role": "user", "content": _input})
        response = model.chat(tokenizer, messages)
        print(response)
        return jsonify({'input':_input,'output':response})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=34503,threaded=True)