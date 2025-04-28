import torch
from typing import List, Dict, Any
import numpy as np
from django.contrib.auth.models import User
from .algorithm import TwinTowerModel
from .dataset import CofounderPairDataset
import logging
from functools import lru_cache
import os

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, model_path: str = 'models/twin_tower.pt'):
        self.model_path = model_path
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = None
        self.dataset = None
        
    @lru_cache(maxsize=1)
    def _load_model(self) -> TwinTowerModel:
        """Load the trained model from disk"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        # load the latest checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        # Initialize model with correct dimensions
        # This should match the dimensions used during training
        model = TwinTowerModel(
            input_dim=384 + 2 + 15,  # BERT dim + numeric dim + categorical dim
            hidden_dims=[512, 256, 128]
        )
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        model.eval()
        
        return model
    
    def _get_dataset(self) -> CofounderPairDataset:
        """Get dataset instance for feature extraction"""
        if self.dataset is None:
            self.dataset = CofounderPairDataset()
        return self.dataset
    
    def _get_user_embedding(self, user_id: int) -> torch.Tensor:
        """Get embedding for a single user"""
        dataset = self._get_dataset()
        return dataset._get_user_embedding(user_id).to(self.device)
    
    def get_recommendations_for_user(
        self,
        user_id: int,
        top_k: int = 10,
        exclude_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top-k recommendations for a user
        
        Args:
            user_id: ID of the user to get recommendations for
            top_k: Number of recommendations to return
            exclude_ids: List of user IDs to exclude from recommendations
            
        Returns:
            List of dictionaries containing recommended users and their scores
        """
        if self.model is None:
            self.model = self._load_model()
            
        # Get target user embedding
        target_embedding = self._get_user_embedding(user_id)
        
        # Get all other user embeddings
        all_users = User.objects.exclude(id=user_id)
        if exclude_ids:
            all_users = all_users.exclude(id__in=exclude_ids)
            
        # Batch process embeddings for efficiency
        batch_size = 32
        recommendations = []
        
        for i in range(0, len(all_users), batch_size):
            batch_users = all_users[i:i + batch_size]
            batch_embeddings = torch.stack([
                self._get_user_embedding(user.id)
                for user in batch_users
            ])
            
            # Compute similarities
            target_embeddings = target_embedding.unsqueeze(0).expand(len(batch_users), -1)
            similarities = self.model.get_similarity(target_embeddings, batch_embeddings)
            
            # Add to recommendations
            for user, score in zip(batch_users, similarities):
                recommendations.append({
                    'user_id': user.id,
                    'score': score.item(),
                    'profile': {
                        'name': user.get_full_name(),
                        'bio': user.profile.bio,
                        'skills': user.profile.skills,
                        'industry': user.profile.industry
                    }
                })
        
        # Sort by score and return top-k
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_k]
    
    def update_recommendations(self):
        """Update recommendations for all users"""
        # this could be implemented as a background task but im too lazy
        # for now, i'll just log that it's called
        logger.info("Updating recommendations for all users") 