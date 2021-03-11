import matplotlib.pyplot as plt
import re
import os

def read_loss(loss_path):
    q_list = list()
    c_list = list()
    with open(loss_path, 'r') as loss_f:
        loss_f.readline()
        i = 0
        for line in loss_f:
            if i % 3 == 1:
                content = line.split(",")
                q = float(content[1].split(":")[1])
                c = float(content[2].split(":")[1])
                q_list.append(q)
                c_list.append(c)
            i += 1
    return q_list, c_list


def read_loss_2(loss_path):
    q_list = list()
    c_list = list()
    with open(loss_path, 'r') as loss_f:
        # loss_f.readline()
        i = 0
        for line in loss_f:
            # print(i, line)
            if i % 2 == 0:
                content = line.split(":")
                q = float(content[1])
                q_list.append(q)
            if i % 2 == 1:
                content = line.split(",")
                c = float(content[0].split(":")[1])
                c_list.append(c)
            i += 1
    return q_list, c_list


def read_sample(sample_file):
    sample_size_list = list()
    time_list = list()
    with open(sample_file, 'r') as sample_f:
        for line in sample_f:
            content = line.split(',')
            time = float(content[0].split(':')[1])
            length = int(content[1].split(':')[1])
            sample_size_list.append(length)
            time_list.append(time)
    return sample_size_list, time_list


def read_train_log(log_file):
    q_list = list()
    c_list = list()
    with open(log_file, 'r') as log_f:
        log_f.readline()
        for line in log_f:
            # print(line)
            if 'epoch' in line and 'loss' not in line:
                content = line.split(",")
                q = float(content[1].split(":")[1])/5
                c = float(content[2].split(":")[1])/5
                # print(q, c)
                q_list.append(q)
                c_list.append(c)
                if len(q_list) >= 10:
                    break
    return q_list, c_list


def read_vary_constraint(file):
    safe_l_list, safe_r_list, p1_list, p2_list = list(), list(), list(), list()
    f = open(file, 'r')
    f.readline()
    name_line = f.readline()
    name_list = name_line[:-1].split(', ')
    name1 = name_list[-2]
    name2 = name_list[-1]
    print(name1, name2)
    for line in f:
        var = line[:-1].split(', ')
        safe_l_list.append(float(var[0]))
        safe_r_list.append(float(var[1]))
        p1_list.append(float(var[2]))
        p2_list.append(float(var[3]))
    return safe_l_list, safe_r_list, p1_list, p2_list, name1, name2


def plot_line(x_list, y_list, title, x_label, y_label, label, fig_title, c='b', log=False):
    ax = plt.subplot(111)
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    plt.plot(x_list, y_list, label=label, c=c)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if log is True:
        plt.yscale("log")

    plt.title(title)
    plt.legend()
    plt.savefig(fig_title)
    plt.close()


def plot_dot(x_list, y_list, title, x_label, y_label, label, fig_title, c='b', log=False):
    ax = plt.subplot(111)
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    plt.plot(x_list, y_list, 'o', label=label, c=c)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if log is True:
        plt.yscale("log")

    plt.title(title)
    plt.legend()
    plt.savefig(fig_title)
    plt.close()


def plot_constraint(x_list, safe_l_list, safe_r_list, p1_list, p2_list, title,  x_label, y_label, label1, label2, fig_title):
    ax = plt.subplot(111)
    ax.get_xaxis().tick_bottom()    
    ax.get_yaxis().tick_left()

    # ax.fill_between(x_list, safe_l_list, safe_r_list, color='C3', alpha=0.5)

    ax.plot(x_list, safe_l_list, color='C3')
    ax.set_ylim([51,54])
    ax.set_ylabel("safe bottom")
    
    ax1 = ax.twinx()
    ax1.plot(x_list, safe_r_list, color='C3')
    ax1.set_ylim([83,86])
    ax1.set_ylabel("safe top")
    # plt.yscale("log")
    ax1.yaxis.grid()
    ax1.xaxis.grid()

    ax2 = ax.twinx()

    ax2.plot(x_list, p1_list, label=label1)
    ax2.plot(x_list, p2_list, label=label2)
    ax2.get_yaxis().set_visible(False)

    ax2.set_xlabel("different constraint")

    # plt.xlabel(x_label)
    # plt.ylabel(y_label)
    
    plt.title(title)
    plt.legend()
    # plt.grid()
    plt.savefig(fig_title)
    plt.close()


def plot_loss(loss_dir):
    for loss_file in os.listdir(loss_dir):
        loss_name = os.path.splitext(loss_file)[0]
        q_list, c_list = read_loss(loss_dir + loss_name + '.txt')
        x_list = list(range(len(q_list)))

        plot_line(x_list, q_list, title=loss_name + ' data loss', x_label='epoch', y_label='loss', label='data loss', fig_title=f"figures/loss/{loss_name}_data_loss.png", c='C0')
        plot_line(x_list, c_list, title=loss_name + ' safe loss', x_label='epoch', y_label='log(loss)', label='safe loss', fig_title=f"figures/loss/{loss_name}_safe_loss.png", c='C1')


def plot_loss_2(loss_dir):
    for loss_file in os.listdir(loss_dir):
        loss_name = os.path.splitext(loss_file)[0]
        q_list, c_list = read_loss_2(loss_dir + loss_name + '.txt')
        x_list = list(range(len(q_list)))

        plot_line(x_list, q_list, title=loss_name + ' data loss', x_label='batch', y_label='log(loss)', label='data loss', fig_title=f"figures/loss/{loss_name}_data_loss.png", c='C0', log=True)
        plot_line(x_list, c_list, title=loss_name + ' safe loss', x_label='batch', y_label='log(loss)', label='safe loss', fig_title=f"figures/loss/{loss_name}_safe_loss.png", c='C1', log=True)
    

def plot_sample(sample_file):
    sample_size_list, time_list = read_sample(sample_file)
    plot_dot(sample_size_list, time_list, title='sample time', x_label='sample size', y_label='time', label='time', fig_title=f"figures/sample/sample_time.png", c='C0')


def plot_training_loss(log_file, benchmark, log=False):
    if log:
        flag = 'log-'
    else:
        flag = ''
    q_list, c_list = read_train_log(log_file)
    x_list = list(range(len(q_list)))

    plot_line(x_list, q_list, title='training data loss', x_label='epoch', y_label=flag + 'loss', label='data loss', fig_title=f"figures/loss/{benchmark}_data_loss.png", c='C0', log=log)
    plot_line(x_list, c_list, title='training safe loss', x_label='epoch', y_label=flag + 'loss', label='safe loss', fig_title=f"figures/loss/{benchmark}_safe_loss.png", c='C1', log=log)


def plot_vary_constraint(file):
    safe_l_list, safe_r_list, p1, p2, name1, name2 = read_vary_constraint(file)
    x_list = list(range(len(safe_l_list)))

    plot_constraint(x_list, safe_l_list, safe_r_list, p1, p2, title='Percentage of Safe Programs with Variable Constraints ',  x_label='constraint', y_label='safe percentage', label1=name1, label2=name2, fig_title=f"figures/vary_constraint_{name1}_{name2}.png")


if __name__ == "__main__":
    # plot_loss('loss/') # the q and c loss
    # plot_loss_2('loss/')
    # plot_sample('data/sample_time.txt')
    # lr_bs_epoch_samplesize
    # plot_training_loss('result/thermostat_nn_volume_[52.0]_[85.1]_0.001_40_10_1000_5000_all_linearrelu.txt', benchmark='thermostat_nn_volume_[52.0]_[85.1]_0.001_40_10_1000_5000_all_linearrelu', log=False)
    plot_vary_constraint('result/vary_constraint_volume_vs_point_sampling.txt')





