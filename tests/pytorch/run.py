import torch

a = torch.FloatTensor([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]).cuda().reshape(2, 3)
b = torch.FloatTensor([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]).cuda().reshape(3, 2)
c = a @ b
print(c.device)
