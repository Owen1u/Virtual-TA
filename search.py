from database import Milvus, BGE
from pprint import pprint
import requests
import json
from collections.abc import Iterable

class MilvusResults():
    def __init__(self,results=None) -> None:
        self.results=[]
        if results:
            for result in results:
                for entry in result:
                    entry_dict={}
                    entry_dict['page'] = entry.entity.get("page")
                    entry_dict['context'] = entry.entity.get("context")
                    entry_dict['distance'] = entry.distance
                    self.results.append(entry_dict)
            self.sorted()
    
    def __add__(self,other):
        res = MilvusResults()
        res.results = self.results+other.results
        res.sorted()
        return res
    
    def sorted(self):
        return self.results.sort(key=lambda x:x['distance'])
    
    def perfect_contexts(self,top_k:int=3,*args,**kw):
        contexts=[]
        for i,res in enumerate(self.results):
            if i >= top_k:
                break
            contexts.append(res['context'])
        return contexts

def clip(x,min,max):
    if x<min:
        x=min
    if x>max:
        x=max
    return x
    
def search(collection_name, input):
    if isinstance(collection_name,str):
        collection_name=[collection_name]
    assert isinstance(collection_name,list)
    
    milvus = Milvus()
    results = MilvusResults()
    for collection in collection_name:
        milvus.load_collection(collection)    # 一个中文占三位
        results += MilvusResults(milvus.search_text('为这个句子生成表示以用于检索相关文章：'+input,top_k=3))

    prompts = results.perfect_contexts(top_k=clip(len(collection_name)*2,3,6))
    prompts = str(prompts)
    print('prompt:',prompts, end='\n\n')

    noun='''
    高斯=Gauss；傅立叶=傅里叶=Fourier；巴特沃斯=Butterworth；贝塞尔=Bessel；拉普拉斯=Laplace；香农=Shannon；
    '''
    
    limit = '你是一个课程助教，只能回答有关学术课程的内容。'
    params = {'input':'以下是检索到课本中的相关内容：\n{1}\n专有名词：{3}\n问题：{0}\n{2}'.format(input,prompts,limit,noun),
           'history': []}
    rl = requests.get('http://58.199.163.176:34503/chat', params=params)
    info = json.loads(rl.text)
    return info['output']


if __name__=='__main__':
    # input = '低通滤波可以用于图像锐化吗？'
    # params = {'input': "问题：{0}\n回答:".format(input),
    #             'history': []}
    # rl = requests.get('http://58.199.163.176:34503/chat', params=params)
    # info = json.loads(rl.text)
    # print(info['output'])
    
    res = search(collection_name = 'jiwang_book_ppt',
           input = '')