import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class Tower(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: list = [512, 256, 128], dropout: float = 0.2):
        super().__init__()
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
            
        # final proj to embedding space
        layers.append(nn.Linear(prev_dim, hidden_dims[-1]))
        
        self.net = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class TwinTowerModel(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dims: list = [512, 256, 128],
        dropout: float = 0.2
    ):
        super().__init__()
        self.tower = Tower(input_dim, hidden_dims, dropout)
        self.embedding_dim = hidden_dims[-1]
        
    def forward(
        self,
        x1: torch.Tensor,
        x2: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through both towers
        
        Args:
            x1: First batch of user embeddings
            x2: Second batch of user embeddings
            
        Returns:
            Tuple of normalized embeddings from both towers
        """
        # get embeddings from both towers
        emb1 = self.tower(x1)
        emb2 = self.tower(x2)
        
        # normalize 'em
        emb1 = F.normalize(emb1, p=2, dim=1)
        emb2 = F.normalize(emb2, p=2, dim=1)
        
        return emb1, emb2
    
    def get_similarity(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """
        Compute cosine similarity between two batches of embeddings
        
        Args:
            x1: First batch of user embeddings
            x2: Second batch of user embeddings
            
        Returns:
            Tensor of cosine similarities
        """
        emb1, emb2 = self.forward(x1, x2)
        return F.cosine_similarity(emb1, emb2, dim=1)
    
    def get_embedding(self, x: torch.Tensor) -> torch.Tensor:
        """
        Get embedding for a single batch of users
        
        Args:
            x: Batch of user embeddings
            
        Returns:
            Normalized embeddings
        """
        emb = self.tower(x)
        return F.normalize(emb, p=2, dim=1) 
    
class HistoryTower(nn.Module):
    """
    Extended tower that encodes both profile features and sequential history.
    """
    def __init__(self, profile_dim: int, history_dim: int, hidden_dim: int = 128, dropout: float = 0.2):
        super().__init__()

        # Profile MLP encoder
        self.profile_mlp = nn.Sequential(
            nn.Linear(profile_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim)
        )

        # GRU-based encoder for sequential history
        self.history_encoder = nn.GRU(
            input_size=history_dim,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True
        )

        # Final fusion layer
        self.combine_layer = nn.Sequential(
            nn.Linear(2 * hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

    def forward(self, profile_feat: torch.Tensor, history_seq: torch.Tensor) -> torch.Tensor:
        # Encode profile features
        profile_emb = self.profile_mlp(profile_feat)

        # Encode sequential history
        _, history_emb = self.history_encoder(history_seq)
        history_emb = history_emb.squeeze(0)  # shape: (batch, hidden_dim)

        # Concatenate and fuse
        combined = torch.cat([profile_emb, history_emb], dim=1)
        out = self.combine_layer(combined)

        return out

class HistoryAwareTwinTowerModel(nn.Module):
    """
    Twin tower model that incorporates user history in the embedding.
    """
    def __init__(
        self,
        profile_dim: int,
        history_dim: int,
        hidden_dim: int = 128,
        dropout: float = 0.2
    ):
        super().__init__()
        self.user_tower = HistoryTower(profile_dim, history_dim, hidden_dim, dropout)
        self.partner_tower = HistoryTower(profile_dim, history_dim, hidden_dim, dropout)

    def forward(
        self,
        x1_profile: torch.Tensor,
        x1_history: torch.Tensor,
        x2_profile: torch.Tensor,
        x2_history: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # Compute embeddings for both user sides
        emb1 = self.user_tower(x1_profile, x1_history)
        emb2 = self.partner_tower(x2_profile, x2_history)

        # Normalize the output embeddings
        emb1 = F.normalize(emb1, p=2, dim=1)
        emb2 = F.normalize(emb2, p=2, dim=1)

        return emb1, emb2

    def get_similarity(self, x1p, x1h, x2p, x2h):
        # Convenience method to compute cosine similarity
        emb1, emb2 = self.forward(x1p, x1h, x2p, x2h)
        return F.cosine_similarity(emb1, emb2, dim=1)

    def get_embedding(self, profile_feat, history_seq):
        # Get embedding for one side
        emb = self.user_tower(profile_feat, history_seq)
        return F.normalize(emb, p=2, dim=1)
