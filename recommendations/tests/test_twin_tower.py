import torch
import pytest
from recommendations.algorithm import TwinTowerModel

@pytest.fixture
def model():
    return TwinTowerModel(input_dim=128, hidden_dims=[64, 32], dropout=0.0, use_faiss=False)

def test_forward_shapes(model):
    x1 = torch.randn(16, 128)
    x2 = torch.randn(16, 128)
    emb1, emb2 = model(x1, x2)
    assert emb1.shape == (16, 32)
    assert emb2.shape == (16, 32)
    # L2-norm ≈ 1
    assert torch.allclose(emb1.norm(dim=1), torch.ones(16), atol=1e-4)

def test_similarity(model):
    x = torch.randn(8, 128)
    sim = model.get_similarity(x, x)
    assert torch.allclose(sim, torch.ones_like(sim), atol=1e-4)
    
def test_faiss_search():
    model = TwinTowerModel(
        input_dim=128,
        hidden_dims=[64, 32],
        use_faiss=True,
        min_data_size_for_ivf=100, 
        nlist=10,  
        nbits=4
    )
    data = torch.randn(500, 128) 
    with torch.no_grad():
        emb = model.get_embedding(data)
    model.init_faiss_index(emb)
    
    query = model.get_embedding(torch.randn(5, 128))
    dist, idx = model.search_similar(query, k=3)
    
    assert idx.shape == (5, 3)
    assert dist.shape == (5, 3)