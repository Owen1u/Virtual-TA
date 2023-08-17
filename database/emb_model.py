from transformers import AutoTokenizer, AutoModel
import torch

class Model():
    def __init__(self) -> None:
        pass
    def load(self,sentences:list[str]):
        pass
    def search(self,sentence:str):
        pass
    
class BGE(Model):
    def __init__(self,model='BAAI/bge-large-zh',
                 path='/nvme01/lmj/virtual-ta/model',
                 device='cpu') -> None:
        super().__init__()
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model,cache_dir=path)
        self.model = AutoModel.from_pretrained(model,cache_dir=path).to(device)
        
    def load(self,sentences):
        with torch.no_grad():
            if isinstance(sentences,str):
                sentences = [sentences]
            encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(self.device)
            model_output = self.model(**encoded_input)
            sentence_embeddings = model_output[0][:, 0]
        return sentence_embeddings.tolist()

        