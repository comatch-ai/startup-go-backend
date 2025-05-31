import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import LinearLR
from typing import Optional
import os
import logging
from datetime import datetime
from .dataset import CofounderPairDataset, CofounderPairDatasetWithHistory
from .algorithm import TwinTowerModel, HistoryAwareTwinTowerModel

class ContrastiveLoss(nn.Module):
    def __init__(self, margin: float = 0.5):
        super().__init__()
        self.margin = margin
        
    def forward(self, x1: torch.Tensor, x2: torch.Tensor, label: torch.Tensor) -> torch.Tensor:
        # cosine similarity
        similarity = F.cosine_similarity(x1, x2, dim=1)
        
        # contrastive loss
        loss = (1 - label) * torch.relu(similarity - self.margin) + \
               label * torch.relu(self.margin - similarity)
               
        return loss.mean()

class Trainer:
    def __init__(
        self,
        model: TwinTowerModel,
        train_dataset: CofounderPairDataset,
        val_dataset: Optional[CofounderPairDataset] = None,
        batch_size: int = 32,
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-5,
        warmup_steps: int = 1000,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        checkpoint_dir: str = 'models'
    ):
        self.model = model.to(device)
        self.device = device
        
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=4
        ) if val_dataset else None
        
        self.criterion = ContrastiveLoss()
        
        self.optimizer = optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        self.scheduler = LinearLR(
            self.optimizer,
            start_factor=0.1,
            end_factor=1.0,
            total_iters=warmup_steps
        )
        
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # setup teh logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def train_epoch(self) -> float:
        self.model.train()
        total_loss = 0
        
        for batch_idx, (x1, x2, label) in enumerate(self.train_loader):
            x1, x2, label = x1.to(self.device), x2.to(self.device), label.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            emb1, emb2 = self.model(x1, x2)
            loss = self.criterion(emb1, emb2, label)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()
            
            total_loss += loss.item()
            
            if batch_idx % 100 == 0:
                self.logger.info(f'Batch {batch_idx}/{len(self.train_loader)} - Loss: {loss.item():.4f}')
                
        return total_loss / len(self.train_loader)
    
    @torch.no_grad()
    def validate(self) -> float:
        if not self.val_loader:
            return float('inf')
            
        self.model.eval()
        total_loss = 0
        
        for x1, x2, label in self.val_loader:
            x1, x2, label = x1.to(self.device), x2.to(self.device), label.to(self.device)
            
            emb1, emb2 = self.model(x1, x2)
            loss = self.criterion(emb1, emb2, label)
            
            total_loss += loss.item()
            
        return total_loss / len(self.val_loader)
    
    def save_checkpoint(self, epoch: int, val_loss: float):
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(self.checkpoint_dir, f'twin_tower_{timestamp}.pt')
        torch.save(checkpoint, path)
        self.logger.info(f'Saved checkpoint to {path}')
        
    def train(self, num_epochs: int, early_stopping_patience: int = 5):
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(num_epochs):
            train_loss = self.train_epoch()
            val_loss = self.validate()
            
            self.logger.info(f'Epoch {epoch + 1}/{num_epochs} - '
                           f'Train Loss: {train_loss:.4f} - '
                           f'Val Loss: {val_loss:.4f}')
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_checkpoint(epoch, val_loss)
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    self.logger.info('Early stopping triggered')
                    break 
                
class TrainerWithHistory:
    def __init__(
        self,
        model: HistoryAwareTwinTowerModel,
        train_dataset: CofounderPairDatasetWithHistory,
        val_dataset: Optional[CofounderPairDatasetWithHistory] = None,
        batch_size: int = 32,
        learning_rate: float = 1e-4,
        weight_decay: float = 1e-5,
        warmup_steps: int = 1000,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        checkpoint_dir: str = 'models'
    ):
        self.model = model.to(device)
        self.device = device

        self.train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4
        )

        self.val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=4
        ) if val_dataset else None

        self.criterion = ContrastiveLoss()
        self.optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        self.scheduler = LinearLR(self.optimizer, start_factor=0.1, end_factor=1.0, total_iters=warmup_steps)

        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def train_epoch(self) -> float:
        self.model.train()
        total_loss = 0

        for batch_idx, (a_profile, a_history, b_profile, b_history, label) in enumerate(self.train_loader):
            a_profile = a_profile.to(self.device)
            a_history = a_history.to(self.device)
            b_profile = b_profile.to(self.device)
            b_history = b_history.to(self.device)
            label = label.to(self.device)

            self.optimizer.zero_grad()
            emb1, emb2 = self.model(a_profile, a_history, b_profile, b_history)
            loss = self.criterion(emb1, emb2, label)
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            total_loss += loss.item()
            if batch_idx % 100 == 0:
                self.logger.info(f'Batch {batch_idx}/{len(self.train_loader)} - Loss: {loss.item():.4f}')

        return total_loss / len(self.train_loader)

    @torch.no_grad()
    def validate(self) -> float:
        if not self.val_loader:
            return float('inf')

        self.model.eval()
        total_loss = 0

        for a_profile, a_history, b_profile, b_history, label in self.val_loader:
            a_profile = a_profile.to(self.device)
            a_history = a_history.to(self.device)
            b_profile = b_profile.to(self.device)
            b_history = b_history.to(self.device)
            label = label.to(self.device)

            emb1, emb2 = self.model(a_profile, a_history, b_profile, b_history)
            loss = self.criterion(emb1, emb2, label)
            total_loss += loss.item()

        return total_loss / len(self.val_loader)

    def save_checkpoint(self, epoch: int, val_loss: float):
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss
        }
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(self.checkpoint_dir, f'history_twin_tower_{timestamp}.pt')
        torch.save(checkpoint, path)
        self.logger.info(f'Saved checkpoint to {path}')

    def train(self, num_epochs: int, early_stopping_patience: int = 5):
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(num_epochs):
            train_loss = self.train_epoch()
            val_loss = self.validate()
            self.logger.info(f'Epoch {epoch + 1}/{num_epochs} - Train Loss: {train_loss:.4f} - Val Loss: {val_loss:.4f}')

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_checkpoint(epoch, val_loss)
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    self.logger.info('Early stopping triggered')
                    break
