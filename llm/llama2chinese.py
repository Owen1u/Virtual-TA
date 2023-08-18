'''
Descripttion: 
version: 
Contributor: Minjun Lu
Source: Original
LastEditTime: 2023-06-22 23:16:48
'''
import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from auto_gptq import AutoGPTQForCausalLM
from flask import Flask,jsonify,request,session
from flask import render_template,make_response
from flask_cors import CORS
import torch.nn as nn
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY']=os.urandom(24)

model = AutoModelForCausalLM.from_pretrained('FlagAlpha/Llama2-Chinese-13b-Chat', device_map='auto',load_in_8bit=True, torch_dtype='auto', cache_dir = '/data/lmj/LLM/download/llama2')
tokenizer = AutoTokenizer.from_pretrained('FlagAlpha/Llama2-Chinese-13b-Chat',use_fast=False, cache_dir = '/data/lmj/LLM/download/llama2')
tokenizer.pad_token = tokenizer.eos_token
@app.route('/chat',methods=['GET','POST'])
def chat():
    if request.method == 'GET':
        _input = str(request.args.get('input'))
        input_ids = tokenizer(['<s>Human: {0}\n</s><s>Assistant: '.format(_input)], return_tensors="pt",add_special_tokens=False).input_ids.to('cuda')
        generate_input = {
            "input_ids":input_ids,
            "max_new_tokens":256,
            "do_sample":True,
            "top_k":50,
            "top_p":0.95,
            "temperature":0.3,
            "repetition_penalty":1.3,
            "eos_token_id":tokenizer.eos_token_id,
            "bos_token_id":tokenizer.bos_token_id,
            "pad_token_id":tokenizer.pad_token_id
        }
        generate_ids  = model.generate(**generate_input)
        text = tokenizer.decode(generate_ids[0])
        print(text)
        return jsonify({'input':_input,'output':text})

# @app.route('/help',methods=['GET','POST'])
# def help():
#     context='''
#     Welcome to GREATLLM!!!
    
#     ip: 58.199.165.40
#     port: 34501
#     model name: ChatGLMv2-7b
#     route: /chatglm2/chat
#     input:{
#         input: str
#         history: list, [[user1,robot1],[user2,robot2],...]
#         **kw
#     }
#     output:{
#         input: str
#         history: list
#         output: str
#     }
    
#     Some ports are available for you to try other models:
#         MPT-7b: 34502
#     '''
#     return jsonify(context)

# @app.route('/chatglm2/chat',methods=['GET'])
# def chat():
#     if request.method == 'GET':
#         _input = str(request.args.get('input'))
#         if request.args.get('history') is not None:
#             _history = request.args.get('history')
#             if isinstance(_history,str):
#                 _history = json.loads(_history)
#         else:
#             _history = []
#         response, history = model_v2.chat(tokenizer_v2, _input, history=_history)
#         return jsonify({'input':_input,'output':response,'history':history})

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=34503,threaded=True)

    
#     pass