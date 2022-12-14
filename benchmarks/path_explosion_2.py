import torch
import torch.nn.functional as F
import torch.nn as nn


import os

index0 = torch.tensor(0)
index1 = torch.tensor(1)
index2 = torch.tensor(2)
index3 = torch.tensor(3)


if torch.cuda.is_available():
    index0 = index0.cuda()
    index1 = index1.cuda()
    index2 = index2.cuda()
    index3 = index3.cuda()


def initialize_components(component_list):
    #TODO: add batched components to replace the following two 
    return states

# input order: h, i
def initialization_abstract_state(component_list):
    abstract_state_list = list()
    # we assume there is only one abstract distribtion, therefore, one component list is one abstract state
    abstract_state = list()
    for component in component_list:
        center, width, p = component['center'], component['width'], component['p']
        symbol_table = {
            'x': domain.Box(var_list([center[0], 0.0]), var_list([width[0], 0.0])),
            'probability': var(p),
            'trajectory': list(),
            'branch': '',
        }
        # print(symbol_table['x'].c, symbol_table['x'].delta)

        abstract_state.append(symbol_table)
    abstract_state_list.append(abstract_state)
    # print(f"finish ini")
    # exit(0)
    return abstract_state_list


def initialization_nn(batched_center, batched_width):
    B, D = batched_center.shape
    padding = torch.zeros(B, 1)
    if torch.cuda.is_available():
        padding = padding.cuda()
    
    input_center, input_width = batched_center[:, :1], batched_width[:, :1]
    symbol_tables = {
        'x': domain.Box(torch.cat((input_center, padding), 1), torch.cat((input_width, padding), 1)),
        'trajectory_list': [[] for i in range(B)],
        'idx_list': [i for i in range(B)], # marks which idx the tensor comes from in the input
    }

    return symbol_tables


def f_test(x):
    return x


class LinearNN(nn.Module):
    def __init__(self, l=1):
        super().__init__()
        self.linear1 = Linear(in_channels=1, out_channels=1)
    
    def forward(self, x):
        res = self.linear1(x)
        return res


class LinearNNComplex(nn.Module):
    def __init__(self, l=4):
        super().__init__()
        self.linear1 = Linear(in_channels=1, out_channels=l)
        self.linear2 = Linear(in_channels=l, out_channels=1)
        self.relu = ReLU()

    def forward(self, x):
        res = self.linear1(x)
        res = self.relu(res)
        res = self.linear2(res)
        return res


def f_assign_h_update(x):
    return x.add(var(0.2))

def f_assign_i_update(x):
    return x.add(var(1.0))

def f_assign_h_increase(x):
    return x.mul(var(2.0)).add(var(1.0))

# input order: 0:h0, 1:bound, 2:count, 3:tmp_h_1, 4:tmp_h_2
class Program(nn.Module):
    def __init__(self, l=1, nn_mode="complex"):
        super(Program, self).__init__()
        self.goal_iteration = var(50.0)
        self.bar1 = var(3.0)
        self.bar2 = var(5.0)
        self.bar3 = var(2.5)

        # simple version
        if nn_mode == "simple":
            self.nn = LinearNN(l=l)
        # complex version
        if nn_mode == "complex":
            self.nn = LinearNNComplex(l=l)

        self.assign_i_update = Assign(target_idx=[1], arg_idx=[1], f=f_assign_i_update)
        self.assign_h_update = Assign(target_idx=[0], arg_idx=[0], f=f_assign_h_update)

        self.assign_h_update_nn = Assign(target_idx=[0], arg_idx=[0], f=self.nn)
        self.assign_skip = Skip()

        self.ifelse_h_block2 = IfElse(target_idx=[0], test=self.bar2, f_test=f_test, body=self.assign_h_update_nn, orelse=self.assign_skip)
        self.ifelse_h = IfElse(target_idx=[0], test=self.bar1, f_test=f_test, body=self.assign_h_update, orelse=self.ifelse_h_block2)

        self.assign_h_increase = Assign(target_idx=[0], arg_idx=[0], f=f_assign_h_increase)
        self.ifelse_h2 = IfElse(target_idx=[0], test=self.bar3, f_test=f_test, body=self.assign_h_increase, orelse=self.assign_skip)
        self.trajectory_update = Trajectory(target_idx=[0])
        self.whileblock = nn.Sequential(
            self.assign_i_update,
            self.assign_h_update,
            self.ifelse_h,
            self.ifelse_h2,
            self.trajectory_update,
        )
        self.while_i = While(target_idx=[1], test=self.goal_iteration, body=self.whileblock)
        self.program = nn.Sequential(
            self.trajectory_update, 
            self.while_i,
        )
    
    def forward(self, input, version=None):
        if version == "single_nn_learning":
            res = self.nn(input)
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








        
