from django.apps import AppConfig
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    
    def ready(self):
        """
        Initialize FAISS index when Django starts
        """
        if not settings.DEBUG:  # 只在生产环境中加载
            try:
                from .service import RecommendationService
                
                # 初始化推荐服务
                service = RecommendationService()
                
                # 从 Git LFS 加载索引
                repo_path = getattr(settings, 'FAISS_INDEX_REPO_PATH', os.path.join(settings.BASE_DIR, 'faiss_indices'))
                index_path = getattr(settings, 'FAISS_INDEX_PATH', 'models/faiss_index')
                branch = getattr(settings, 'FAISS_INDEX_BRANCH', 'main')
                
                success = service.load_faiss_index_from_git_lfs(
                    repo_path=repo_path,
                    index_path=index_path,
                    branch=branch
                )
                
                if success:
                    logger.info("Successfully loaded FAISS index on startup")
                else:
                    logger.warning("Failed to load FAISS index on startup")
                    
            except Exception as e:
                logger.error(f"Error initializing FAISS index: {e}")