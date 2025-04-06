# main.py
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
import os
import sys

# 添加项目根目录到Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 初始化Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
import django
django.setup()

# 导入本地模块
from KGRS.kg_builder import build_knowledge_graph, save_kg  # 使用绝对导入
from KGRS.transE import train_transE
from KGRS.mkr import MKR, train_mkr

def prepare_mkr_data(entity2id, transE_model):
    """
    准备MKR训练数据：
    1. 用户特征：已选课程数量、学习时长等
    2. 课程特征：核心概念数量、视频数量等
    3. 知识嵌入：TransE生成的课程实体嵌入
    """
    # 示例数据生成（需根据实际数据替换）
    n_samples = 1000
    user_feat = np.random.randn(n_samples, 5)  # 5维用户特征
    item_feat = np.random.randn(n_samples, 10)  # 10维课程特征
    kg_emb = transE_model.entity_emb(torch.LongTensor(list(entity2id.values())))
    labels = np.random.randint(0, 2, n_samples)  # 二分类标签

    # 转换为Tensor
    dataset = TensorDataset(
        torch.FloatTensor(user_feat),
        torch.FloatTensor(item_feat),
        kg_emb.repeat(n_samples // len(entity2id) + 1, 1)[:n_samples],
        torch.FloatTensor(labels)
    )

    # 划分训练测试集
    train_size = int(0.8 * n_samples)
    train_set, test_set = torch.utils.data.random_split(dataset, [train_size, n_samples - train_size])

    return DataLoader(train_set, batch_size=32), DataLoader(test_set, batch_size=32)


if __name__ == "__main__":
    # 步骤1：构建知识图谱
    kg_triples = build_knowledge_graph()
    save_kg(kg_triples, "knowledge_graph.tsv")

    # 步骤2：训练TransE模型
    transE_model, entity2id, _ = train_transE(kg_triples)

    # 步骤3：准备MKR数据并训练
    train_loader, test_loader = prepare_mkr_data(entity2id, transE_model)
    mkr_model = MKR(user_dim=5, item_dim=10, kg_emb_dim=128)
    train_mkr(mkr_model, train_loader, test_loader)

    # 步骤4：生成推荐
    # （需要实现具体推荐逻辑，此处为示例）
    user_feat = torch.randn(1, 5)
    item_feat = torch.randn(10, 10)
    scores = mkr_model(user_feat, item_feat, transE_model.entity_emb.weight)
    top_items = torch.argsort(scores, descending=True)[:5]
    print(f"推荐课程ID: {[list(entity2id.keys())[i] for i in top_items]}")