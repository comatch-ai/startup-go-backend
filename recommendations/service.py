import torch
from typing import List, Dict, Any
import numpy as np
from django.contrib.auth.models import User
from .algorithm import TwinTowerModel
from .dataset import CofounderPairDataset
from .faiss_utils import FAISSIndexManager
import logging
from functools import lru_cache
import os
from django.conf import settings

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, model_path: str = 'models/twin_tower.pt'):
        self.model_path = model_path
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = None
        self.dataset = None
        self.index_manager = None
        
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
    
    def load_faiss_index_from_git_lfs(self, repo_path: str, index_path: str, branch: str = 'main') -> bool:
        """
        Load FAISS index from Git LFS
        
        Args:
            repo_path: Path to the Git repository
            index_path: Relative path to the index file
            branch: Git branch to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.index_manager is None:
                # 初始化 FAISS 索引管理器
                # 使用与 TwinTowerModel 相同的维度
                self.index_manager = FAISSIndexManager(
                    embedding_dim=384 + 2 + 15,  # BERT dim + numeric dim + categorical dim
                    min_data_size_for_ivf=getattr(settings, 'FAISS_MIN_DATA_SIZE', 10000),
                    nlist=getattr(settings, 'FAISS_NLIST', 100),
                    nprobe=getattr(settings, 'FAISS_NPROBE', 10),
                    nbits=getattr(settings, 'FAISS_NBITS', 8),
                    use_gpu=self.device == 'cuda'
                )
            
            return self.index_manager.load_index_from_git_lfs(repo_path, index_path, branch)
            
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return False
            
    def save_faiss_index_to_git_lfs(self, repo_path: str, index_path: str, commit_message: str = "Update FAISS index") -> bool:
        """
        Save FAISS index to Git LFS
        
        Args:
            repo_path: Path to the Git repository
            index_path: Relative path to save the index
            commit_message: Git commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.index_manager is None:
                logger.error("No FAISS index manager initialized")
                return False
                
            return self.index_manager.save_index_to_git_lfs(repo_path, index_path, commit_message)
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            return False
            
    def _update_faiss_index(self):
        """Update FAISS index with current user embeddings"""
        if self.index_manager is None:
            logger.error("No FAISS index manager initialized")
            return False
            
        try:
            # 获取所有用户的嵌入
            all_users = User.objects.all()
            embeddings = []
            
            for user in all_users:
                embedding = self._get_user_embedding(user.id)
                embeddings.append(embedding)
                
            # 更新索引
            embeddings = torch.stack(embeddings)
            self.index_manager.init_index(embeddings)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update FAISS index: {e}")
            return False
    
    def update_recommendations(self):
        """Update recommendations for all users"""
        try:
            # 更新 FAISS 索引
            if self._update_faiss_index():
                logger.info("Successfully updated FAISS index")
            else:
                logger.warning("Failed to update FAISS index")
                
            # 这里可以添加其他更新逻辑
            logger.info("Updating recommendations for all users")
            
        except Exception as e:
            logger.error(f"Error updating recommendations: {e}")
            raise 