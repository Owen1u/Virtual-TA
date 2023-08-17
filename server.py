import os
import json
from flask import Flask,jsonify,request,session
from flask import render_template,make_response
from flask_cors import CORS
from database import Milvus, BGE
from paddleocr import PaddleOCR,PPStructure
from search import search

COURSES = ['shutu','jiwang','xinhao']

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY']=os.urandom(24)

embed_model = BGE(model = 'BAAI/bge-large-zh',
            path = '/nvme01/lmj/virtual-ta/model',
            device = 'cuda:0')
paddle_ocr = PaddleOCR(use_angle_cls=False, lang="ch",use_gpu=True)
paddle_structure = PPStructure(use_gpu=True)

@app.route('/embed',methods=['POST'])
def embed():
    if request.method == 'POST':
        _input = json.loads(request.data)['input']
        if isinstance(_input,str):
            _input = [_input]
        assert isinstance(_input,list),'input must be a LIST!'
        embeddings = embed_model.load(_input)
        return jsonify({'input':_input,'output':embeddings})
    
@app.route('/ppocr',methods=['POST'])     
def ppocr():
    if request.method == 'POST':
        _input = request.files["image"].read()
        output = paddle_ocr.ocr(_input)
        return jsonify({'output':output})

@app.route('/ppstructure',methods=['POST'])     
def ppstructure():
    if request.method == 'POST':
        _input = request.files["image"].read()
        output = paddle_structure(_input)
        results = [{'bbox':region['bbox'],'type':region['type']} for region in output]
        return jsonify({'output':results})

@app.route('/QA/all',methods=['GET'])
def all():
    if request.method == 'GET':
        _input = request.args.get('input')
        output = search(['{0}_book_ppt'.format(course) for course in COURSES],_input)
        results = dict(input=_input, output=output)
        return jsonify(results)


for course in COURSES:
    code = '''
@app.route('/QA/{0}',methods=['GET'])
def {0}():
    if request.method == 'GET':
        _input = request.args.get('input')
        output = search('{0}_book_ppt',_input)
        results = dict(input=_input, output=output)
        return jsonify(results)'''.format(course)
    exec(code)

@app.route('/')
def index():
    resp = make_response(render_template("index.html"))
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=34510,threaded=True)