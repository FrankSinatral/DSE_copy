import random
from random import shuffle
import pandas as pd
import numpy as np
import time
from timeit import default_timer as timer

from constants import *


def load_data(
    train_size,
    test_size,
    dataset_path,
    ):
    start_t = time.time()
    f = open(dataset_path, 'r')
    f.readline()
    data_list = list()
    for line in f:
        content = line[:-2].split(';')
        trajectory_list = list()
        for state_content in content:
            # print(state_content)
            state_content = state_content[2:-2].split('], [')
            state_list, action_list = state_content[0], state_content[1]
            # one state is represented by state, action, label
            state = [float(v) for v in state_list.split(',')]
            #print(f"state is:{state}")
            action = [float(v) for v in action_list.split(',')]
            #print(f"action is:{action}")
            trajectory_list.append([state, action])
        data_list.append(trajectory_list)

    # do not use random shuffle, bugs
    # data_list = np.array(data_list)
    # print(f"data:\n {data_list[0][0]}\n{data_list[1][0]}\n{data_list[2][0]}")
    np.random.shuffle(data_list)
    # print(f"data after shuffle:\n {data_list[0][0]}\n{data_list[1][0]}\n{data_list[2][0]}")
    trajectory_train_list = data_list[:train_size]
    trajectory_test_list = data_list[train_size:train_size + test_size]
    print(f"train tra length: {len(trajectory_train_list)}, test tra length: {len(trajectory_test_list)}")
    # print(trajectory_train_list[0])
    # print(trajectory_test_list)
    # exit(0)
    # X_train, X_test, y_train, y_test
    print("---Data Generation---")
    print("--- %s seconds ---" % (time.time() - start_t))
    # return train_list[:, 0], test_list[:, 0], train_list[:, 1], test_list[:, 1]
    # print(f"train list: {[k[0] for k in trajectory_train_list]}")
    # print(f"trajectory train: trajectory_train_list")
    # exit(0)
    return trajectory_train_list, trajectory_test_list