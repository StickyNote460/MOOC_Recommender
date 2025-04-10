# KGRS/mkr.py
import torch
import torch.nn as nn


class MKR(nn.Module):
    """多任务知识感知推荐模型"""

    def __init__(self, user_dim, item_dim, kg_emb_dim, hidden_dim=64):
        super().__init__()
        # 用户-课程交互模块
        self.user_net = nn.Sequential(
            nn.Linear(user_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, kg_emb_dim)
        )
        # 课程特征网络
        self.item_net = nn.Sequential(
            nn.Linear(item_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, kg_emb_dim)
        )
        # 知识图谱融合层
        self.kge_fc = nn.Linear(kg_emb_dim * 2, kg_emb_dim)

    def forward(self, user_feat, item_feat, kg_emb):
        # 用户和课程嵌入
        user_emb = self.user_net(user_feat)
        item_emb = self.item_net(item_feat)

        # 知识增强的交互
        combined = torch.cat([user_emb * kg_emb, item_emb * kg_emb], dim=1)
        fused = self.kge_fc(combined)
        return torch.sigmoid(fused.sum(dim=1))