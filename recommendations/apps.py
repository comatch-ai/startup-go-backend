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
        if not settings.DEBUG:  
            try:
                from .service import RecommendationService
                
                # Initialize recommendation service
                service = RecommendationService()
                
                # Load index from Git LFS 
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