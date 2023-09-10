MILVUS_IP = "10.0.0.5"
MILVUS_PORT = "19530"

from PIL import Image
import requests
import json
import io
from collections.abc import Iterable
from typing import Optional,Union

def image2bytes(image:Image.Image):
    img_bytes = io.BytesIO()
    image = image.convert("RGB")
    image.save(img_bytes, format="JPEG")
    data = img_bytes.getvalue()
    return data

def api_ppocr(image:Image.Image):
    file = {'image': image2bytes(image)}
    rl = requests.post('http://127.0.0.1:34510/ppocr', files=file)
    info = json.loads(rl.text)
    return info['output']

def api_ppstructure(image:Image.Image):
    file = {'image': image2bytes(image)}
    rl = requests.post('http://127.0.0.1:34510/ppstructure', files=file)
    info = json.loads(rl.text)
    return info['output']

def api_embed(input:Union[str,list]):
    data = {'input':input}
    embeddings = requests.post('http://127.0.0.1:34510/embed', data=json.dumps(data))
    embeddings = json.loads(embeddings.text)['output']
    return embeddings

def api_llm(input:str,history:list=[]):
    params = {'input': input,
              'history': history}
    rl = requests.get('http://10.0.0.20:34503/chat', params=params)
    info = json.loads(rl.text)
    output = info['output']
    return output