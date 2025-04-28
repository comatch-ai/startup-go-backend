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