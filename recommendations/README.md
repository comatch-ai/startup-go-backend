# Cofounder Matching Recommendation System (draft 1 paul)

This module implements a deep learning-based recommendation system for matching cofounders using a twin-tower embedding model.

## Architecture

The recommendation system consists of several key components:

1. **Data Pipeline** (`dataset.py`)
   - `CofounderPairDataset`: Handles data loading and preprocessing
   - Converts user profiles to feature vectors using text embeddings and feature engineering

2. **Model** (`algorithm.py`)
   - `TwinTowerModel`: Implements the twin-tower architecture
   - Uses shared MLP towers to generate user embeddings
   - Computes cosine similarity between embeddings

3. **Training** (`train.py`)
   - `Trainer`: Handles model training and validation
   - Implements contrastive loss for learning embeddings
   - Includes early stopping and checkpointing

4. **Service Layer** (`service.py`)
   - `RecommendationService`: Manages model inference
   - Handles batch processing for efficient recommendations
   - Caches model and embeddings for performance

## API Endpoints

- `GET /api/recommendations/get_recommendations/`
  - Returns personalized recommendations for the current user
  - Returns top 10 matches by default

- `POST /api/recommendations/update_recommendations/`
  - Triggers model retraining
  - Updates recommendations for all users

## Training the Model

1. Prepare the data:
   ```python
   from recommendations.dataset import CofounderPairDataset
   from recommendations.algorithm import TwinTowerModel
   from recommendations.train import Trainer

   # Create dataset
   dataset = CofounderPairDataset()
   
   # Initialize model
   model = TwinTowerModel(
       input_dim=384 + 2 + 15,  # BERT dim + numeric dim + categorical dim
       hidden_dims=[512, 256, 128]
   )
   
   # Create trainer
   trainer = Trainer(
       model=model,
       train_dataset=dataset,
       batch_size=32,
       learning_rate=1e-4
   )
   
   # Train model
   trainer.train(num_epochs=50)
   ```

2. Monitor training:
   - Checkpoints are saved in the `models/` directory
   - Training logs show loss metrics and validation performance

## Serving Recommendations

1. Load the trained model:
   ```python
   from recommendations.service import RecommendationService
   
   service = RecommendationService()
   ```

2. Get recommendations:
   ```python
   recommendations = service.get_recommendations_for_user(
       user_id=123,
       top_k=10
   )
   ```

## FAISS Indexing

To accelerate nearest-neighbor search over the learned user embeddings, the system
integrates **FAISS** (Facebook AI Similarity Search).

### Installation

Only CPU-only version is implemented:

```bash
# CPU version (cross-platform)
pip install faiss-cpu

# GPU version (requires CUDA)
pip install faiss-gpu    # CUDA >= 11.2
```

macOS note: If you hit an OpenMP duplicate-runtime error, add
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
to ~/.zshrc and reload (source ~/.zshrc). See the Troubleshooting section.

### Run test for FAISS
Run the following command from the project root:

```bash
pytest
```


## Monitoring

The system includes basic logging and monitoring:
- Training progress and metrics
- Inference latency
- Error tracking

## Dependencies

- PyTorch ≥1.12.0
- sentence-transformers
- Django REST Framework
- NumPy
- pytest-pythonpath
- pytest-django

## Notes

- The model uses GPU acceleration if available
- Text features are encoded using BERT embeddings
- Numeric features are normalized
- Categorical features use one-hot encoding
- The system supports incremental updates and retraining 