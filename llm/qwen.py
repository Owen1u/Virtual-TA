import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig
from flask import Flask,jsonify,request,session
from flask import render_template,make_response
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY']=os.urandom(24)

# Note: The default behavior now has injection attack prevention off.
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-7B-Chat", trust_remote_code=True,cache_dir='/data/lmj/LLM/download')

# use bf16
# model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat", device_map="auto", trust_remote_code=True, bf16=True).eval()
# use fp16
# model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat", device_map="auto", trust_remote_code=True, fp16=True).eval()
# use cpu only
# model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat", device_map="cpu", trust_remote_code=True).eval()
# use auto mode, automatically select precision based on the device.
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat", device_map="auto", trust_remote_code=True,cache_dir='/data/lmj/LLM/download').eval()
model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-7B-Chat", trust_remote_code=True,cache_dir='/data/lmj/LLM/download')

@app.route('/chat',methods=['GET'])
def chat():
    if request.method == 'GET':
        _input = str(request.args.get('input'))
        if request.args.get('history') is not None:
            _history = request.args.get('history')
            if isinstance(_history,str):
                _history = json.loads(_history)
        else:
            _history = []
        response, history = model.chat(tokenizer, _input, history=_history)
        return jsonify({'input':_input,'output':response,'history':history})

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=34503,threaded=True)