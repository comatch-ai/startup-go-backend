import torch
from algorithm import HistoryAwareTwinTowerModel

def main():
    profile_dim = 64
    history_dim = 384
    history_len = 5
    batch_size = 4

    model = HistoryAwareTwinTowerModel(profile_dim=profile_dim, history_dim=history_dim)
    model.eval()

    # Fake profile and history inputs
    a_profile = torch.randn(batch_size, profile_dim)
    b_profile = torch.randn(batch_size, profile_dim)
    a_history = torch.randn(batch_size, history_len, history_dim)
    b_history = torch.randn(batch_size, history_len, history_dim)

    # Get similarity scores
    sim_random = model.get_similarity(a_profile, a_history, b_profile, b_history)
    sim_self = model.get_similarity(a_profile, a_history, a_profile, a_history)

    print("Profiles are", "≠" if not torch.allclose(a_profile, b_profile) else "=", "each other")
    print("Sim (random) ≈", sim_random.tolist())
    print("Sim (self) ≈", sim_self.tolist())

if __name__ == "__main__":
    main()
