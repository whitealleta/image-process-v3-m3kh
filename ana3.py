
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import time


# Step 2: Load the pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Step 4: Preprocess the text
df = pd.read_excel(r'output_part_1.xlsx')


def npl_simi(content):
    time.sleep(1)
    outputs_list = []
    for text in content:
            inputs = tokenizer(text[:500], return_tensors="pt")
            outputs = model(**inputs)
            outputs_list.append(outputs)

    # 提取最后一层的隐藏状态
    last_hidden_states = [outputs.last_hidden_state.view(outputs.last_hidden_state.size(0), -1).detach().numpy() for
                          outputs in outputs_list]

    # 转换为numpy数组
    arrays = [array for array in last_hidden_states]
    max_length = min([array.shape[1] for array in arrays])  # 找到最小长度
    arrays_processed = [array[:, :max_length] for array in arrays]  # 截断或填充到最小长度

    # 计算余弦相似度
    similarity_scores = cosine_similarity(np.concatenate(arrays_processed))

    # 转换为相似度值列表
    similarity_scores_list = similarity_scores.tolist()
    similarity_scores_list_2 = [np.mean(similarity_scores) for similarity_scores in similarity_scores_list]
    return similarity_scores_list_2

try:

    # 对于每个组，使用npl_simi函数计算相似度并展平
    df['相似度'] = df.groupby('汽车品牌')['评论内容'].transform(lambda x: np.array(npl_simi(x)).flatten())
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    df.to_excel('dongchedi/output_with_similarity_car_comments.xlsx_1', index= False)