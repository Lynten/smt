# coding=utf-8
import codecs
from sys import argv, exit

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

START_INDEX = 1


def main():
    if len(argv) < 5:
        exit('Usage: %s e_token_file f_token_file aligned_file line_to_plot' % argv[0])

    _, e_token_file, f_token_file, aligned_file, line_to_plot = argv

    # Prepare data
    e_sentence = ''
    f_sentence = ''
    point_indices = ''
    with codecs.open(e_token_file, encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx == int(line_to_plot):
                e_sentence = line
                break

    with codecs.open(f_token_file, encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx == int(line_to_plot):
                f_sentence = line
                break
    with open(aligned_file) as f:
        for idx, line in enumerate(f):
            if idx == int(line_to_plot):
                points = line.strip().split()
                if START_INDEX:
                    points = map(lambda p: (int(p[0]) - 1, int(p[1]) - 1), [point.split('-') for point in points])
                else:
                    points = map(lambda p: (int(p[0]), int(p[1])), [point.split('-') for point in points])

                point_indices = list(zip(*points))
                break

    x_ticks = e_sentence.split()
    y_ticks = f_sentence.split()

    align_matrix = np.zeros(shape=(len(y_ticks), len(x_ticks)))
    align_matrix[point_indices] = 1

    # Plot
    fig, ax = plt.subplots()

    plt.imshow(align_matrix, cmap='binary')
    plt.xticks(np.arange(len(x_ticks)), x_ticks, rotation=90)
    plt.yticks(np.arange(len(y_ticks)), y_ticks)

    ax.set_xticks(np.arange(len(x_ticks)) + 0.5, minor=True)  # Grid lines
    ax.set_yticks(np.arange(len(y_ticks)) + 0.5, minor=True)
    ax.xaxis.grid(True, which='minor')
    ax.yaxis.grid(True, which='minor')

    ax.xaxis.set_ticks_position('top')

    plt.show()


if __name__ == '__main__':
    main()
