# KGRS/transE.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


class KGDataset(Dataset):
    """知识图谱数据集加载器"""

    def __init__(self, triples, entity2id, relation2id):
        self.triples = [
            (entity2id[h], relation2id[r], entity2id[t])
            for h, r, t in triples
            if h in entity2id and t in entity2id and r in relation2id
        ]

    def __len__(self):
        return len(self.triples)

    def __getitem__(self, idx):
        return torch.LongTensor(self.triples[idx])


class TransE(nn.Module):
    """TransE知识嵌入模型"""

    def __init__(self, num_entities, num_relations, emb_dim=128, margin=1.0):
        super().__init__()
        self.emb_dim = emb_dim
        self.margin = margin
        self.entity_emb = nn.Embedding(num_entities, emb_dim)
        self.relation_emb = nn.Embedding(num_relations, emb_dim)
        nn.init.xavier_uniform_(self.entity_emb.weight)
        nn.init.xavier_uniform_(self.relation_emb.weight)

    def forward(self, pos_triples, neg_triples=None):
        h_pos = self.entity_emb(pos_triples[:, 0])
        r_pos = self.relation_emb(pos_triples[:, 1])
        t_pos = self.entity_emb(pos_triples[:, 2])
        pos_score = torch.norm(h_pos + r_pos - t_pos, p=2, dim=1)

        if neg_triples is not None:
            h_neg = self.entity_emb(neg_triples[:, 0])
            r_neg = self.relation_emb(neg_triples[:, 1])
            t_neg = self.entity_emb(neg_triples[:, 2])
            neg_score = torch.norm(h_neg + r_neg - t_neg, p=2, dim=1)
            loss = torch.mean(torch.relu(self.margin + pos_score - neg_score))
        else:
            loss = torch.mean(pos_score)

        return loss


def train_transE(kg_triples, epochs=100, batch_size=1024):
    """训练TransE模型"""
    # 构建实体和关系映射
    entities = set([h for h, _, _ in kg_triples] + [t for _, _, t in kg_triples])
    relations = set([r for _, r, _ in kg_triples])
    entity2id = {e: i for i, e in enumerate(entities)}
    relation2id = {r: i for i, r in enumerate(relations)}

    # 数据加载
    dataset = KGDataset(kg_triples, entity2id, relation2id)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 模型初始化
    model = TransE(len(entity2id), len(relation2id))
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 训练循环
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            # 负采样（随机替换头实体）
            neg_batch = batch.clone()
            neg_batch[:, 0] = torch.randint(0, len(entity2id), (batch.size(0),))

            # 计算损失
            optimizer.zero_grad()
            loss = model(batch, neg_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"Epoch {epoch + 1}/{epochs} | Loss: {total_loss / len(dataloader):.4f}")

    return model, entity2id, relation2id