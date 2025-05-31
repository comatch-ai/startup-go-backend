import torch
from torch.utils.data import Dataset
from sentence_transformers import SentenceTransformer
from django.contrib.auth.models import User
from .models import Recommendation
import numpy as np
from typing import Tuple, List, Dict
import torch.nn.functional as F

class CofounderPairDataset(Dataset):
    def __init__(
        self,
        text_encoder: str = 'all-MiniLM-L6-v2',
        max_length: int = 128,
        negative_ratio: float = 1.0
    ):
        self.text_encoder = SentenceTransformer(text_encoder)
        self.max_length = max_length
        self.negative_ratio = negative_ratio
        
        # Load all user profiles
        self.users = list(User.objects.all())
        self.user_profiles = {user.id: self._get_user_features(user) for user in self.users}
        
        # Get positive pairs from recommendations
        self.positive_pairs = self._get_positive_pairs()
        
    def _get_user_features(self, user: User) -> Dict:
        """Extract and preprocess user features"""
        profile = user.profile
        
        # Text features
        text_features = {
            'skills': profile.skills or '',
            'bio': profile.bio or '',
            'industry': profile.industry or '',
            'role_interest': profile.role_interest or ''
        }
        
        # Numeric features
        numeric_features = {
            'years_experience': profile.years_experience or 0,
            'num_projects': profile.num_projects or 0
        }
        
        # Categorical features
        categorical_features = {
            'location': profile.location or '',
            'education_level': profile.education_level or ''
        }
        
        return {
            'text': text_features,
            'numeric': numeric_features,
            'categorical': categorical_features
        }
    
    def _get_positive_pairs(self) -> List[Tuple[int, int]]:
        """Get positive pairs from recommendations"""
        positive_pairs = []
        for rec in Recommendation.objects.all():
            positive_pairs.append((rec.user.id, rec.project.user.id))
        return positive_pairs
    
    def _encode_text(self, text_features: Dict) -> torch.Tensor:
        """Encode text features using sentence transformer"""
        texts = [text_features[k] for k in ['skills', 'bio', 'industry', 'role_interest']]
        embeddings = self.text_encoder.encode(texts, convert_to_tensor=True)
        return embeddings.mean(dim=0)
    
    def _normalize_numeric(self, numeric_features: Dict) -> torch.Tensor:
        """Normalize numeric features"""
        features = torch.tensor([
            numeric_features['years_experience'],
            numeric_features['num_projects']
        ], dtype=torch.float32)
        return F.normalize(features, dim=0)
    
    def _encode_categorical(self, categorical_features: Dict) -> torch.Tensor:
        """One-hot encode categorical features"""
        # simplified version - in production, we'd want to use learned embeddings
        location_embedding = torch.zeros(10)  # assuming 10 possible locations
        education_embedding = torch.zeros(5)  # assuming 5 education levels
        
        # set appropriate indices to 1
        # this is a placeholder - implement proper encoding based on your categories
        return torch.cat([location_embedding, education_embedding])
    
    def _get_user_embedding(self, user_id: int) -> torch.Tensor:
        """Get complete user embedding"""
        profile = self.user_profiles[user_id]
        
        text_embedding = self._encode_text(profile['text'])
        numeric_embedding = self._normalize_numeric(profile['numeric'])
        categorical_embedding = self._encode_categorical(profile['categorical'])
        
        return torch.cat([text_embedding, numeric_embedding, categorical_embedding])
    
    def __len__(self) -> int:
        return len(self.positive_pairs) * (1 + int(self.negative_ratio))
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Get positive pair
        pos_idx = idx % len(self.positive_pairs)
        user_a_id, user_b_id = self.positive_pairs[pos_idx]
        
        # Get embeddings
        embedding_a = self._get_user_embedding(user_a_id)
        embedding_b = self._get_user_embedding(user_b_id)
        
        # Create label (1 for positive pairs)
        label = torch.tensor(1.0)
        
        return embedding_a, embedding_b, label 
    
class CofounderPairDatasetWithHistory(Dataset):
    def __init__(self, text_encoder: str = 'all-MiniLM-L6-v2', history_max_len: int = 5):
        self.text_encoder = SentenceTransformer(text_encoder)
        self.users = list(User.objects.all())
        self.user_profiles = {user.id: self._get_user_features(user) for user in self.users}
        self.user_histories = {user.id: self._get_user_history(user) for user in self.users}
        self.positive_pairs = self._get_positive_pairs()
        self.history_max_len = history_max_len

    def _get_user_features(self, user: User) -> Dict:
        profile = user.profile
        text_features = {
            'skills': profile.skills or '',
            'bio': profile.bio or '',
            'industry': profile.industry or '',
            'role_interest': profile.role_interest or ''
        }
        return text_features

    def _get_user_history(self, user: User) -> List[str]:
        recs = Recommendation.objects.filter(user=user).order_by('-created_at')[:self.history_max_len]
        texts = []
        for rec in recs:
            try:
                partner_profile = rec.project.user.profile
                text = f"{partner_profile.skills or ''}, {partner_profile.bio or ''}"
                texts.append(text)
            except Exception:
                continue
        return texts

    def _get_positive_pairs(self) -> List[Tuple[int, int]]:
        return [(rec.user.id, rec.project.user.id) for rec in Recommendation.objects.all()]

    def _get_user_embedding(self, user_id: int) -> Tuple[torch.Tensor, torch.Tensor]:
        text_feat = self.user_profiles[user_id]
        history_feat = self.user_histories[user_id]

        profile_embedding = self.text_encoder.encode(
            [text_feat[k] for k in ['skills', 'bio', 'industry', 'role_interest']], convert_to_tensor=True
        ).mean(dim=0)

        if len(history_feat) == 0:
            history_embedding = torch.zeros_like(profile_embedding)
        else:
            history_embedding = self.text_encoder.encode(history_feat, convert_to_tensor=True).mean(dim=0)

        return profile_embedding, history_embedding

    def __len__(self):
        return len(self.positive_pairs)

    def __getitem__(self, idx: int):
        user_a_id, user_b_id = self.positive_pairs[idx]
        a_profile, a_history = self._get_user_embedding(user_a_id)
        b_profile, b_history = self._get_user_embedding(user_b_id)
        label = torch.tensor(1.0)
        return a_profile, a_history, b_profile, b_history, label
    