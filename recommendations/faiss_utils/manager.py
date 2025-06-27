import faiss
import numpy as np
import torch
from typing import Optional, Tuple, Union, List
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class FAISSIndexManager:
    """Manager class for FAISS index operations"""
    
    def __init__(
        self,
        embedding_dim: int,
        min_data_size_for_ivf: int = 10000,
        nlist: int = 100,
        nprobe: int = 10,
        nbits: int = 8,
        use_gpu: bool = False
    ):
        """
        Initialize FAISS index manager
        
        Args:
            embedding_dim: Dimension of the embeddings
            min_data_size_for_ivf: Minimum data size to use IVF index
            nlist: Number of clusters for IVF
            nprobe: Number of clusters to probe during search
            nbits: Number of bits per code for PQ
            use_gpu: Whether to use GPU for FAISS operations
        """
        self.embedding_dim = embedding_dim
        self.min_data_size_for_ivf = min_data_size_for_ivf
        self.nlist = nlist
        self.nprobe = nprobe
        self.nbits = nbits
        self.use_gpu = use_gpu
        self.index = None
        self.embeddings = None
        
    def create_index(self, data_size: int) -> faiss.Index:
        """
        Create appropriate FAISS index based on data size
        
        Args:
            data_size: Size of the dataset
            
        Returns:
            FAISS index instance
        """
        if data_size < self.min_data_size_for_ivf:
            logger.info(f"Small dataset ({data_size} < {self.min_data_size_for_ivf}), using IndexFlatL2")
            index = faiss.IndexFlatL2(self.embedding_dim)
        else:
            logger.info(f"Large dataset ({data_size} >= {self.min_data_size_for_ivf}), using IndexIVFPQ")
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            index = faiss.IndexIVFPQ(
                quantizer,
                self.embedding_dim,
                self.nlist,
                8,  # number of sub-quantizers
                self.nbits
            )
            
        if self.use_gpu:
            try:
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
                logger.info("Using GPU for FAISS operations")
            except Exception as e:
                logger.warning(f"Failed to use GPU: {e}. Falling back to CPU.")
                
        return index
        
    def init_index(self, embeddings: Union[torch.Tensor, np.ndarray]):
        """
        Initialize index with embeddings
        
        Args:
            embeddings: Input embeddings (torch.Tensor or numpy.ndarray)
        """
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.detach().cpu().numpy().astype('float32')
            
        data_size = embeddings.shape[0]
        self.index = self.create_index(data_size)
        
        if isinstance(self.index, faiss.IndexIVFPQ) and not self.index.is_trained:
            self.index.train(embeddings)
            
        self.index.add(embeddings)
        self.embeddings = embeddings
        
    def add_to_index(self, embeddings: Union[torch.Tensor, np.ndarray]):
        """
        Add new embeddings to the index
        
        Args:
            embeddings: New embeddings to add
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call init_index first.")
            
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.detach().cpu().numpy().astype('float32')
            
        # Check if we need to switch to IVF index
        if isinstance(self.index, faiss.IndexFlatL2):
            total_size = (self.embeddings.shape[0] if self.embeddings is not None else 0) + embeddings.shape[0]
            if total_size >= self.min_data_size_for_ivf:
                logger.info(f"Data size reached threshold ({total_size} >= {self.min_data_size_for_ivf}), switching to IndexIVFPQ")
                # Save existing data
                old_embeddings = self.embeddings
                if old_embeddings is not None:
                    old_embeddings = np.concatenate([old_embeddings, embeddings])
                else:
                    old_embeddings = embeddings
                    
                # Reinitialize index
                self.init_index(old_embeddings)
                return
                
        # Normal data addition
        self.index.add(embeddings)
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.concatenate([self.embeddings, embeddings])
            
    def search(
        self,
        query_embeddings: Union[torch.Tensor, np.ndarray],
        k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar embeddings
        
        Args:
            query_embeddings: Query embeddings
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple of (distances, indices)
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call init_index first.")
            
        if isinstance(query_embeddings, torch.Tensor):
            query_embeddings = query_embeddings.detach().cpu().numpy().astype('float32')
            
        # Set nprobe for IVF index
        if isinstance(self.index, faiss.IndexIVFPQ):
            self.index.nprobe = self.nprobe
            
        return self.index.search(query_embeddings, k)
        
    def load_index_from_git_lfs(self, repo_path: str, index_path: str, branch: str = 'main') -> bool:
        """
        Load index from Git LFS storage
        
        Args:
            repo_path: Path to the Git repository
            index_path: Relative path to the index file in the repository
            branch: Git branch to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure we're in the correct directory
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Pull the latest changes
            subprocess.run(['git', 'pull', 'origin', branch], check=True)
            
            # Ensure Git LFS is initialized
            subprocess.run(['git', 'lfs', 'install'], check=True)
            
            # Pull the LFS objects
            subprocess.run(['git', 'lfs', 'pull'], check=True)
            
            # Construct full path to index file
            full_index_path = os.path.join(repo_path, index_path)
            
            # Load the index
            self.load_index(full_index_path)
            
            # Return to original directory
            os.chdir(original_dir)
            
            logger.info(f"Successfully loaded index from Git LFS: {index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index from Git LFS: {e}")
            # Return to original directory in case of error
            os.chdir(original_dir)
            return False
            
    def save_index_to_git_lfs(self, repo_path: str, index_path: str, commit_message: str = "Update FAISS index") -> bool:
        """
        Save index to Git LFS storage
        
        Args:
            repo_path: Path to the Git repository
            index_path: Relative path to save the index file
            commit_message: Git commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure we're in the correct directory
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            # Save the index
            full_index_path = os.path.join(repo_path, index_path)
            self.save_index(full_index_path)
            
            # Track the file with Git LFS
            subprocess.run(['git', 'lfs', 'track', index_path], check=True)
            
            # Add and commit the changes
            subprocess.run(['git', 'add', '.gitattributes', index_path], check=True)
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push changes
            subprocess.run(['git', 'push', 'origin', 'HEAD'], check=True)
            
            # Return to original directory
            os.chdir(original_dir)
            
            logger.info(f"Successfully saved index to Git LFS: {index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save index to Git LFS: {e}")
            # Return to original directory in case of error
            os.chdir(original_dir)
            return False
            
    def save_index(self, path: str):
        """
        Save the index to disk
        
        Args:
            path: Path to save the index
        """
        if self.index is None:
            raise ValueError("No index to save")
            
        # TODO: When migrating to cloud storage (S3/GCS/OSS), 
        # modify this method to use the cloud storage client.
        # The interface should remain the same, only the storage backend needs to change.
        if isinstance(self.index, faiss.IndexIVFPQ):
            # For IVF index, we need to save both the index and the embeddings
            faiss.write_index(self.index, f"{path}.index")
            np.save(f"{path}.embeddings.npy", self.embeddings)
        else:
            faiss.write_index(self.index, path)
            
    def load_index(self, path: str):
        """
        Load the index from disk
        
        Args:
            path: Path to load the index from
        """
        # TODO: When migrating to cloud storage (S3/GCS/OSS),
        # modify this method to use the cloud storage client.
        # The interface should remain the same, only the storage backend needs to change.
        try:
            self.index = faiss.read_index(f"{path}.index")
            self.embeddings = np.load(f"{path}.embeddings.npy")
        except:
            # Try loading as a simple index
            self.index = faiss.read_index(path)
            self.embeddings = None 