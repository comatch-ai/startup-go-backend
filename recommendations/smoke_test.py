import torch
from algorithm import TwinTowerModel

def main():
    input_dim = 64
    batch_size = 4

    model = TwinTowerModel(input_dim=input_dim)
    model.eval()

    x1 = torch.randn(batch_size, input_dim)
    x2 = torch.randn(batch_size, input_dim)

    # compare x1 vs x2
    sims_random = model.get_similarity(x1, x2)
    # compare x1 vs itself
    sims_self   = model.get_similarity(x1, x1)

    print("x1 and x2 are", "≠" if not torch.allclose(x1, x2) else "=", "each other")
    print("sims_random (should hover ~0):", sims_random.tolist())
    print("sims_self   (should be all 1.0):",   sims_self.tolist())

if __name__ == "__main__":
    main()
