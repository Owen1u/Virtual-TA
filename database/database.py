from pymilvus import connections, utility
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection
from torch.utils.data import DataLoader
import torch
from tqdm import tqdm
from text2vec import SentenceModel
from transformers import AutoTokenizer, AutoModel
from .emb_model import Model
import requests
import json

class Milvus():
    def __init__(self,model:Model=None, 
                 host:str="58.199.162.205", 
                 port:str="19530") -> None:
        connections.connect(host=host, port=port)
        self.model = model
        
    def load_model(self):
        pass
        # self.sim_model = SentenceModel("shibing624/text2vec-base-chinese-paraphrase",cache_dir='/nvme01/lmj/virtual-ta/model')
        
    def list_collections(self):
        return utility.list_collections()
    
    def drop_collection(self,collection_name):
        utility.drop_collection(collection_name)
        
    def create_collection(self,collection_name,type='image',dimension:int=2048, index_type="IVF_FLAT",max_length:int=200):
        assert index_type in ['FLAT','IVF_FLAT','IVF_SQ8','IVF_PQ','HNSW','ANNOY'], '''
        FLAT is best suited for scenarios that seek perfectly accurate and exact search results on a small, million-scale dataset.
        IVF_FLAT is a quantization-based index and is best suited for scenarios that seek an ideal balance between accuracy and query speed.
        IVF_SQ8 is a quantization-based index and is best suited for scenarios that seek a significant reduction on disk, CPU, and GPU memory consumption as these resources are very limited.
        IVF_PQ is a quantization-based index and is best suited for scenarios that seek high query speed even at the cost of accuracy.
        HNSW is a graph-based index and is best suited for scenarios that have a high demand for search efficiency.
        ANNOY is a tree-based index and is best suited for scenarios that seek a high recall rate.
        '''
        assert not utility.has_collection(collection_name),'Collection已存在'
        if type== 'image':
            fields = [
                FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='filepath', dtype=DataType.VARCHAR, max_length=max_length),  # VARCHARS need a maximum length, so for this example they are set to 200 characters
                FieldSchema(name='page', dtype=DataType.INT64, max_length=max_length),
                FieldSchema(name='image_embedding', dtype=DataType.FLOAT_VECTOR, dim=dimension)
            ]
        elif type == 'text':
            fields = [
                FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='context', dtype=DataType.VARCHAR, max_length=max_length),  # VARCHARS need a maximum length, so for this example they are set to 200 characters
                FieldSchema(name='page', dtype=DataType.INT64),
                FieldSchema(name='text_embedding', dtype=DataType.FLOAT_VECTOR, dim=dimension)
            ]
        schema = CollectionSchema(fields=fields)
        self.collection = Collection(name=collection_name, schema=schema)
        index_params = {
            'metric_type':'L2',
            'index_type':index_type,
            'params':{'nlist': 16384}
            }
        if type== 'image':
            self.collection.create_index(field_name="image_embedding", index_params=index_params)
        elif type == 'text':
            self.collection.create_index(field_name="text_embedding", index_params=index_params)
        print('collection 「{}」 has {} entities'.format(collection_name,self.collection.num_entities))
    
    def load_collection(self,collection_name,**kw):
        assert utility.has_collection(collection_name),'Collection不存在'
        self.collection = Collection(name=collection_name)
        print('collection 「{}」 has {} entities'.format(collection_name,self.collection.num_entities))
    
    def model_forward(self,input):
        if self.model:
            embeddings = self.model.load(input)
        else:
            data = {'input':input}
            embeddings = requests.post('http://127.0.0.1:34510/embed', data=json.dumps(data))
            embeddings = json.loads(embeddings.text)['output']
        return embeddings
    
    def load_text(self,sentences,page:int):
        self.collection.load()
        embeddings = self.model_forward(sentences)
        self.collection.insert([list(sentences), list([page]*len(sentences)),embeddings])
        self.collection.flush()
    
    def search_text(self,sentence,top_k=3,output_fields=['context','page']):
        embeddings = self.model_forward(sentence)
        result = self.collection.search(embeddings, anns_field='text_embedding', param={'nprobe': 512}, limit=top_k, output_fields=output_fields)
        return result
    
    
    # def search_text_by_page(self,sentence:str,page:int,limit=5,output_fields=['context','page']):
    #     with torch.no_grad():
    #         # output = self.sim_model.encode(sentence)
    #         # output = torch.from_numpy(output).squeeze()
    #         # output = output.unsqueeze(0)
    #         sentences=[sentence]
    #         encoded_input = self.bge_tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(self.device)
    #         model_output = self.bge_model(**encoded_input)
    #         sentence_embeddings = model_output[0][:, 0]
    #     return self.collection.search(sentence_embeddings.tolist(), anns_field='text_embedding', param={'nprobe': 512},limit=limit,expr= "{0} <= page <= {1}".format(page-1,page+1), output_fields=output_fields)
    
