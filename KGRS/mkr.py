# mkr.py
# KGRS/mkr.py
import torch
import torch.nn as nn

class MKR(nn.Module):
    """推荐模型"""
class MKR(nn.Module):
    """
    Multi-Task Feature Learning for Knowledge Graph Enhanced Recommendation
    输入:
        user_features: 用户特征向量 [batch_size, user_dim]
        item_features: 课程特征向量 [batch_size, item_dim]
        kg_embeddings: TransE生成的实体嵌入
    """

    def __init__(self, user_dim, item_dim, kg_emb_dim, hidden_dim=64):
        super().__init__()

        # 用户-课程推荐模块
        self.user_net = nn.Sequential(
            nn.Linear(user_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, kg_emb_dim)
        )

        self.item_net = nn.Sequential(
            nn.Linear(item_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, kg_emb_dim)
        )

        # 知识图谱嵌入模块
        self.kge_net = nn.Sequential(
            nn.Linear(kg_emb_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, kg_emb_dim)
        )

    def forward(self, user_features, item_features, kg_embeddings):
        # 用户和课程嵌入
        user_emb = self.user_net(user_features)
        item_emb = self.item_net(item_features)

        # 知识增强的特征交互
        kg_user = torch.cat([user_emb, kg_embeddings], dim=1)
        kg_item = torch.cat([item_emb, kg_embeddings], dim=1)
        kg_fusion = self.kge_net(kg_user + kg_item)

        # 预测得分
        prediction = torch.sigmoid(torch.sum(user_emb * kg_fusion * item_emb, dim=1))
        return prediction


def train_mkr(model, train_loader, test_loader, n_epochs=50, optim=None):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(n_epochs):
        model.train()
        train_loss = 0
        for user_feat, item_feat, kg_emb, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(user_feat, item_feat, kg_emb)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # 验证步骤
        model.eval()
        test_loss = 0
        with torch.no_grad():
            for user_feat, item_feat, kg_emb, labels in test_loader:
                outputs = model(user_feat, item_feat, kg_emb)
                test_loss += criterion(outputs, labels).item()

        print(
            f"Epoch {epoch + 1} | Train Loss: {train_loss / len(train_loader):.4f} | Test Loss: {test_loss / len(test_loader):.4f}")