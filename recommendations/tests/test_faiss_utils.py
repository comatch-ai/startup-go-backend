import pytest
import torch
import numpy as np
from ..faiss_utils import FAISSIndexManager

@pytest.fixture
def small_embeddings():
    """Generate small test embeddings"""
    return torch.randn(100, 128)  # 100 samples, 128 dimensions

@pytest.fixture
def large_embeddings():
    """Generate large test embeddings"""
    return torch.randn(20000, 128)  # 20000 samples, 128 dimensions

@pytest.fixture
def index_manager():
    """Create a FAISSIndexManager instance"""
    return FAISSIndexManager(
        embedding_dim=128,
        min_data_size_for_ivf=10000,
        nlist=100,
        nprobe=10,
        nbits=8
    )

def test_init_index_small_dataset(index_manager, small_embeddings):
    """Test index initialization with small dataset"""
    index_manager.init_index(small_embeddings)
    assert isinstance(index_manager.index, faiss.IndexFlatL2)
    assert index_manager.embeddings.shape == (100, 128)

def test_init_index_large_dataset(index_manager, large_embeddings):
    """Test index initialization with large dataset"""
    index_manager.init_index(large_embeddings)
    assert isinstance(index_manager.index, faiss.IndexIVFPQ)
    assert index_manager.embeddings.shape == (20000, 128)

def test_add_to_index_small_to_large(index_manager, small_embeddings):
    """Test adding embeddings that trigger index type switch"""
    # Initial small dataset
    index_manager.init_index(small_embeddings)
    assert isinstance(index_manager.index, faiss.IndexFlatL2)
    
    # Add more data to trigger switch
    large_addition = torch.randn(10000, 128)
    index_manager.add_to_index(large_addition)
    assert isinstance(index_manager.index, faiss.IndexIVFPQ)
    assert index_manager.embeddings.shape == (10100, 128)

def test_search(index_manager, small_embeddings):
    """Test similarity search"""
    index_manager.init_index(small_embeddings)
    
    # Create query embeddings
    query = torch.randn(5, 128)
    
    # Search
    distances, indices = index_manager.search(query, k=3)
    
    # Check output shapes
    assert distances.shape == (5, 3)
    assert indices.shape == (5, 3)
    assert np.all(indices >= 0) and np.all(indices < 100)

def test_save_load_index(index_manager, small_embeddings, tmp_path):
    """Test saving and loading index"""
    # Initialize and save
    index_manager.init_index(small_embeddings)
    save_path = str(tmp_path / "test_index")
    index_manager.save_index(save_path)
    
    # Create new manager and load
    new_manager = FAISSIndexManager(embedding_dim=128)
    new_manager.load_index(save_path)
    
    # Verify index type and data
    assert isinstance(new_manager.index, type(index_manager.index))
    if isinstance(index_manager.index, faiss.IndexIVFPQ):
        assert new_manager.embeddings is not None
        assert new_manager.embeddings.shape == index_manager.embeddings.shape

def test_gpu_support():
    """Test GPU support if available"""
    try:
        manager = FAISSIndexManager(
            embedding_dim=128,
            use_gpu=True
        )
        embeddings = torch.randn(1000, 128)
        manager.init_index(embeddings)
        
        # If we get here, GPU initialization was successful
        assert manager.index is not None
    except Exception as e:
        # Skip test if GPU is not available
        pytest.skip(f"GPU not available: {str(e)}")

def test_error_handling(index_manager):
    """Test error handling for invalid operations"""
    # Test search without initialization
    with pytest.raises(ValueError):
        index_manager.search(torch.randn(5, 128))
    
    # Test add without initialization
    with pytest.raises(ValueError):
        index_manager.add_to_index(torch.randn(5, 128))
    
    # Test save without initialization
    with pytest.raises(ValueError):
        index_manager.save_index("test")

def test_numpy_input(index_manager):
    """Test handling of numpy array inputs"""
    embeddings = np.random.randn(100, 128).astype('float32')
    index_manager.init_index(embeddings)
    
    # Test search with numpy input
    query = np.random.randn(5, 128).astype('float32')
    distances, indices = index_manager.search(query, k=3)
    assert distances.shape == (5, 3)
    assert indices.shape == (5, 3)

def test_batch_operations(index_manager, small_embeddings):
    """Test batch operations"""
    index_manager.init_index(small_embeddings)
    
    # Test batch search
    batch_queries = torch.randn(10, 128)
    distances, indices = index_manager.search(batch_queries, k=5)
    assert distances.shape == (10, 5)
    assert indices.shape == (10, 5)
    
    # Test batch add
    batch_add = torch.randn(50, 128)
    index_manager.add_to_index(batch_add)
    assert index_manager.embeddings.shape[0] == 150  # 100 + 50 