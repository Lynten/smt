#!/usr/bin/env python

# Fork from https://github.com/adasikow/dtau-python-grow-diag-final

from itertools import izip
import re
from sys import argv, exit

# 0 - include alignments to 'NULL' token in GROW-DIAG-FINAL
# 1 - exclude alignments to 'NULL' token in GROW-DIAG-FINAL
START_INDEX = 1


def init_matrix(rows, columns, value):
    """
    A function that returns matrix in a given
    dimensions filled with a given value
    """

    result = [[value for _ in range(columns)] for _ in range(rows)]
    return result


def intersection(e2f, f2e):
    rows = len(e2f)
    columns = len(f2e)
    result = init_matrix(rows, columns, False)
    for e in range(rows):
        for f in range(columns):
            result[e][f] = e2f[e][f] and f2e[f][e]

    return result


def union(e2f, f2e):
    rows = len(e2f)
    columns = len(f2e)
    result = init_matrix(rows, columns, False)
    for e in range(rows):
        for f in range(columns):
            result[e][f] = e2f[e][f] or f2e[f][e]

    return result


def neighboring_points((e_index, f_index), e_len, f_len):
    """
    A function that returns list of neighboring points in
    an alignment matrix for a given alignment (pair of indexes)
    """
    result = []

    if e_index > 0:
        result.append((e_index - 1, f_index))
    if f_index > 0:
        result.append((e_index, f_index - 1))
    if e_index < e_len - 1:
        result.append((e_index + 1, f_index))
    if f_index < f_len - 1:
        result.append((e_index, f_index + 1))
    if e_index > 0 and f_index > 0:
        result.append((e_index - 1, f_index - 1))
    if e_index > 0 and f_index < f_len - 1:
        result.append((e_index - 1, f_index + 1))
    if e_index < e_len - 1 and f_index > 0:
        result.append((e_index + 1, f_index - 1))
    if e_index < e_len - 1 and f_index < f_len - 1:
        result.append((e_index + 1, f_index + 1))

    return result


def aligned_e(e, f_len, alignment):
    """
    A function that checks if a given 'english' word is aligned
    to any foreign word in a given foreign sentence
    """
    for f in range(START_INDEX, f_len):
        if alignment[e][f]:
            return True

    return False


def aligned_f(f, e_len, alignment):
    """
    A function that checks if a given foreign word is aligned
    to any 'english' word in a given 'english' sentence
    """
    for e in range(START_INDEX, e_len):
        if alignment[e][f]:
            return True

    return False


def grow_diag(union, alignment, e_len, f_len):
    new_points_added = True
    while new_points_added:
        new_points_added = False
        for e in range(START_INDEX, e_len):
            for f in range(START_INDEX, f_len):
                if alignment[e][f]:
                    for (e_new, f_new) in neighboring_points((e, f), e_len, f_len):
                        if not (aligned_e(e_new, f_len, alignment) and aligned_f(f_new, e_len, alignment)) \
                                and union[e_new][f_new]:
                            alignment[e_new][f_new] = True
                            new_points_added = True


def final(alignment, e2f, f2e, e_len, f_len):
    """
    A function that implements both FINAL(e2f) and FINAL(f2e)
    steps of GROW-DIAG-FINAL algorithm
    """
    for e in range(START_INDEX, e_len):
        for f in range(START_INDEX, f_len):
            if not (aligned_e(e, f_len, alignment) and aligned_f(f, e_len, alignment)) \
                    and (e2f[e][f] or f2e[f][e]):
                alignment[e][f] = True


def final_e2f(alignment, e2f, e_len, f_len):
    """
    A function that implements FINAL(e2f) step of GROW-DIAG-FINAL algorithm
    """
    for e in range(START_INDEX, e_len):
        for f in range(START_INDEX, f_len):
            if not (aligned_e(e, f_len, alignment) and aligned_f(f, e_len, alignment)) \
                    and e2f[e][f]:
                alignment[e][f] = True


def final_f2e(alignment, f2e, e_len, f_len):
    """
    A function that implements FINAL(f2e) step of GROW-DIAG-FINAL algorithm
    """
    for e in range(START_INDEX, e_len):
        for f in range(START_INDEX, f_len):
            if not (aligned_e(e, f_len, alignment) and aligned_f(f, e_len, alignment)) \
                    and f2e[f][e]:
                alignment[e][f] = True


def grow_diag_final(e2f, f2e, e_len, f_len):
    alignment = intersection(e2f, f2e)
    grow_diag(union(e2f, f2e), alignment, e_len, f_len)
    final(alignment, e2f, f2e, e_len, f_len)
    return alignment


def parse_alignments(alignments_line, values):
    word_alignments_regex = ur"(\S+)\s\(\{([\s\d]*)\}\)"
    alignments = re.findall(word_alignments_regex, alignments_line)

    # Initialize matrix with False value for each pair of words
    rows = len(alignments)
    columns = len(values)
    result = init_matrix(rows, columns, False)

    # Align words
    for i in range(len(alignments)):
        alignment_values = alignments[i][1].split()
        for alignment in alignment_values:
            result[i][int(alignment)] = True

    return result


def print_alignments(alignments, e_len, f_len):
    result = ''
    for f in range(1, f_len):
        for e in range(1, e_len):
            if alignments[e][f]:
                result += str(f) + '-' + str(e) + ' '

    print result.strip()


def main():
    if len(argv) < 3:
        exit('Usage: %s e2f_alignments_file f2e_alignments_file' % argv[0])

    script, e2f_filename, f2e_filename = argv

    # States:
    # 0 - skip line with information about sentences length and alignment score
    # 1 - read sentences
    # 2 - read alignments and run GROW-DIAG-FINAL
    state = 0

    e_sentence = []
    f_sentence = []

    with open(e2f_filename) as e2f_file, open(f2e_filename) as f2e_file:
        for e2f_line, f2e_line in izip(e2f_file, f2e_file):
            if state == 0:
                state = 1
            elif state == 1:
                f_sentence = ['NULL'] + e2f_line.split()
                e_sentence = ['NULL'] + f2e_line.split()
                state = 2
            elif state == 2:
                alignments = grow_diag_final(
                    parse_alignments(e2f_line, f_sentence),
                    parse_alignments(f2e_line, e_sentence),
                    len(e_sentence), len(f_sentence))
                print_alignments(alignments, len(e_sentence), len(f_sentence))
                state = 0


if __name__ == '__main__':
    main()
