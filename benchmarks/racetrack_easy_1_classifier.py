import torch
import torch.nn as nn

import constants
from constants import *
import domain

import os

if constants.status == 'train':
    if mode == 'DSE':
        from gpu_DSE.modules import *
    elif mode == 'only_data':
        # print(f"in only data: import DSE_modules")
        from gpu_DSE.modules import *
    elif mode == 'DiffAI':
        from gpu_DiffAI.modules import *
    elif mode == 'symbol_data_loss_DSE':
        from gpu_symbol_data_loss_DSE.modules import *
    elif mode == 'DiffAI_sps':
        from gpu_DiffAI_sps.modules import *
elif constants.status == 'verify_AI':
    # print(f"in verify_AI: modules_AI")
    from modules_AI import *
elif constants.status == 'verify_SE':
    # print(f"in verify_SE: modules_SE")
    from modules_SE import *

index0 = torch.tensor(0)
index1 = torch.tensor(1)
index2 = torch.tensor(2)
index3 = torch.tensor(3)
min_v = torch.tensor(-10.0)
max_v = torch.tensor(10.0)

if torch.cuda.is_available():
    index0 = index0.cuda()
    index1 = index1.cuda()
    index2 = index2.cuda()
    index3 = index3.cuda()
    min_v = min_v.cuda()
    max_v = max_v.cuda()


# x, y, p0, p1, p2, i
def initialize_components(abstract_states):
    center, width = abstract_states['center'], abstract_states['width']
    B, D = center.shape
    padding = torch.zeros(B, 1)
    if torch.cuda.is_available():
        padding = padding.cuda()
    
    input_center, input_width = center[:, :1], width[:, :1]
    states = {
        'x': domain.Box(torch.cat((input_center, padding, padding, padding, padding, padding), 1), \
            torch.cat((input_width, padding, padding, padding, padding, padding), 1)),
        'trajectories': [[] for i in range(B)],
        'idx_list': [i for i in range(B)],
        'p_list': [var(0.0) for i in range(B)], # might be changed to batch
        'alpha_list': [var(1.0) for i in range(B)],
    }

    return states

# input order: x, y, z
def initialization_components_point():
    B = 5
    input_center, input_width, padding = torch.zeros(B, 1), torch.zeros(B, 1), torch.zeros(B, 1)
    if torch.cuda.is_available():
        padding = padding.cuda()
        input_center = input_center.cuda()
        input_width = input_width.cuda()
    
    input_center[0], input_width[0] = 4.1, 0.0
    input_center[3], input_width[3] = 4.0005, 0.0005 
    input_center[1], input_width[1] = 5.0, 0.0
    input_center[2], input_width[2] = 5.0, 0.0005
    input_center[4], input_width[4] = 4.001, 0.0

    states = {
        'x': domain.Box(torch.cat((input_center, padding, padding, padding, padding, padding), 1), \
            torch.cat((input_width, padding, padding, padding, padding, padding), 1)),
        'trajectories': [[] for i in range(B)],
        'idx_list': [i for i in range(B)],
        'p_list': [var(0.0) for i in range(B)], # might be changed to batch
        'alpha_list': [var(1.0) for i in range(B)],
    }

    return states

def f_test(x):
    return x


class LinearNN(nn.Module):
    def __init__(self, l=1):
        super().__init__()
        self.linear1 = Linear(in_channels=2, out_channels=3)
    
    def forward(self, x):
        res = self.linear1(x)
        return res


class LinearNNComplex(nn.Module):
    def __init__(self, l=4):
        super().__init__()
        self.linear1 = Linear(in_channels=2, out_channels=l)
        self.linear2 = Linear(in_channels=l, out_channels=l)
        self.linear3 = Linear(in_channels=l, out_channels=3)
        self.relu = ReLU()
        self.sigmoid = Sigmoid()

    def forward(self, x):
        res = self.linear1(x)
        res = self.relu(res)
        res = self.linear2(res)
        res = self.relu(res)
        res = self.linear3(res)
        res = self.sigmoid(res)
        return res


def f_move_up(x):
    return x.sub_l(var(1.0))
def f_move_right(x):
    return x
def f_move_down(x):
    return x.add(var(1.0))

def f_forward(x): # y += 1
    return x.add(var(1.0))
def f_step_update(x):
    return x.add(var(1.0))

class Program(nn.Module):
    def __init__(self, l=1, nn_mode="simple"):
        super(Program, self).__init__()
        self.step = var(19)
        if nn_mode == "simple":
            self.nn = LinearNN(l=l)
        if nn_mode == "complex":
            self.nn = LinearNNComplex(l=l)

        self.move_down = Assign(target_idx=[0], arg_idx=[0], f=f_move_down)
        self.move_right = Assign(target_idx=[0], arg_idx=[0], f=f_move_right)
        self.move_up = Assign(target_idx=[0], arg_idx=[0], f=f_move_up)
        
        self.assign_branch_probability = Assign(target_idx=[2, 3, 4], arg_idx=[0, 1], f=self.nn)
        self.argmax_p = ArgMax(arg_idx=[2, 3, 4], branch_list=[self.move_up, self.move_right, self.move_down])

        self.forward_update = Assign(target_idx=[1], arg_idx=[1], f=f_forward)
        self.step_update = Assign(target_idx=[5], arg_idx=[5], f=f_step_update)
        self.trajectory_update = Trajectory(target_idx=[0, 1, 2, 3, 4]) # x, y, angle

        self.whileblock = nn.Sequential(
            self.assign_branch_probability, # x, y -> p0, p1, p2
            self.argmax_p,
            self.forward_update,  # update y: y += 1
            self.step_update, # update step i
            self.trajectory_update, 
        )
        self.program = While(target_idx=[5], test=self.step, body=self.whileblock)
    
    def forward(self, input, version=None):
        if version == "single_nn_learning":
            # model the car-controller
            y = self.nn(input)
            # print(self.nn.linear1.weight.detach().cpu().numpy().tolist())
            # print(self.nn.linear2.weight.detach().cpu().numpy().tolist())
            # exit(0)
            res = y
        else:
            res = self.program(input)
        return res

    def clip_norm(self):
        if not hasattr(self, "weight"):
            return
        if not hasattr(self, "weight_g"):
            if torch.__version__[0] == "0":
                nn.utils.weight_norm(self, dim=None)
            else:
                nn.utils.weight_norm(self)


def load_model(m, folder, name, epoch=None):
    if os.path.isfile(folder):
        m.load_state_dict(torch.load(folder))
        return None, m
    model_dir = os.path.join(folder, f"model_{name}")
    if not os.path.exists(model_dir):
        return None, None
    if epoch is None and os.listdir(model_dir):
        epoch = max(os.listdir(model_dir), key=int)
    path = os.path.join(model_dir, str(epoch))
    if not os.path.exists(path):
        return None, None
    m.load_state_dict(torch.load(path))
    return int(epoch), m


def save_model(model, folder, name, epoch):
    path = os.path.join(folder, f"model_{name}", str(epoch))
    try:
        os.makedirs(os.path.dirname(path))
    except FileExistsError:
        pass
    torch.save(model.state_dict(), path)









        
