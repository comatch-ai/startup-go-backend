from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
    # 添加 FAISS 索引管理相关的端点
    path('faiss/status/', RecommendationViewSet.as_view({'get': 'get_faiss_status'}), name='faiss-status'),
    path('faiss/reload/', RecommendationViewSet.as_view({'post': 'reload_faiss_index'}), name='faiss-reload'),
    path('faiss/update/', RecommendationViewSet.as_view({'post': 'update_faiss_index'}), name='faiss-update'),
]