'''
Descripttion: 
version: 
Contributor: Minjun Lu
Source: Original
LastEditTime: 2023-06-22 23:16:48
'''
import os
import json
from transformers import AutoModel
from transformers import AutoTokenizer
from flask import Flask,jsonify,request,session
from flask import render_template,make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY']=os.urandom(24)

tokenizer_v2 = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True,cache_dir='/data/lmj/LLM/download/ChatGLM/v2')
model_v2 = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True,cache_dir='/data/lmj/LLM/download/ChatGLM/v2').cuda()

@app.route('/help',methods=['GET','POST'])
def help():
    context='''
    Welcome to GREATLLM!!!
    
    ip: 58.199.165.40
    port: 34501
    model name: ChatGLMv2-7b
    route: /chatglm2/chat
    input:{
        input: str
        history: list, [[user1,robot1],[user2,robot2],...]
        **kw
    }
    output:{
        input: str
        history: list
        output: str
    }
    
    Some ports are available for you to try other models:
        MPT-7b: 34502
    '''
    return jsonify(context)

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
        response, history = model_v2.chat(tokenizer_v2, _input, history=_history)
        return jsonify({'input':_input,'output':response,'history':history})

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=34503,threaded=True)
    # Hou: 34510-34539
    # Wang: 34540-34569
    # Chai: 34570-34599