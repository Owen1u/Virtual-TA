from utils import PDF,PPT
from database import Milvus, BGE
from tqdm import tqdm

SENTENCE_MAX_LENGTH = 250
DIM = 1024
COLLECTION_NAME = 'xinhao_book_ppt'

# model = BGE(model = 'BAAI/bge-large-zh',
#             path = '/nvme01/lmj/virtual-ta/model',
#             device = 'cuda:0')

milvus = Milvus()
# milvus.drop_collection(COLLECTION_NAME)
milvus.load_collection(COLLECTION_NAME, type='text', dimension = DIM,max_length=SENTENCE_MAX_LENGTH * 3)    # 一个中文占三位

def load_pdf(path):
    pdf = PDF(path = path, max_length = SENTENCE_MAX_LENGTH)
    with tqdm(total=len(pdf),desc='loading',ncols=80) as bar:
        for idx, contexts in enumerate(pdf):
            page = idx + 1
            if contexts:
                milvus.load_text(contexts, page)
            print(contexts)
            bar.update(1)

def load_ppt(path):
    ppt = PPT(path,max_length = SENTENCE_MAX_LENGTH)
    with tqdm(total=len(ppt),desc='loading',ncols=80) as bar:
        for contexts,page in ppt:
            print(contexts)
            bar.update(1)
            
if __name__=='__main__':
    load_pdf('/nvme01/lmj/virtual-ta/data/信号/book_2.pdf')
    # load_ppt(path='/nvme01/lmj/virtual-ta/data/数图习题2023.pptx')