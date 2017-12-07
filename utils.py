"""Utility module"""
import numpy as np
from math import sqrt, log

def calculate_jacard_coeff(q_set, t_set):
        """Calculates jacard coefficient using alternate
           definition of union"""
        n = len(q_set.intersection(t_set))
        return n / float(len(q_set) + len(t_set) - n)


def edit_dist(qword, tword):
    """Calculates the Levenshtein edit distance
        between two words using Dynamic Programming"""
    if len(qword) < len(tword):
        return edit_dist(tword, qword)
    if len(tword) == 0:
        return len(qword)
    qword = np.array(tuple(qword))
    tword = np.array(tuple(tword))
    previous_row = np.arange(tword.size + 1)
    for s in qword:
        current_row = previous_row + 1
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], tword != s))
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)
        previous_row = current_row
    return previous_row[-1]


def intersect_sorted_lists(list_one, list_two):
    """Intersects two sorted lists"""
    if not (list_one and list_two):
        return
    iter_one = iter(list_one)
    iter_two = iter(list_two)
    left = next(iter_one)
    right = next(iter_two)
    cur = -1
    while True:
        try:
            if left < right:
                left = next(iter_one)
            if right < left:
                right = next(iter_two)
            if right == left:
                yield right
                right = next(iter_two)
        except StopIteration:
            break


def union_sorted_lists(list_one, list_two):
    """Combines two sorted lists while removing duplicates"""
    if not list_one:
        for a in list_two:
            yield a
        return
    if not list_two:
        for a in list_one:
            yield a
        return
    iter_one = iter(list_one)
    iter_two = iter(list_two)
    left = next(iter_one)
    right = next(iter_two)
    cur = -1
    while True:
        if left < right:
            if left > cur:
                cur = left
                yield cur
            try:
                left = next(iter_one)
            except StopIteration:
                last = right
                iter_one = iter_two
                break
        else:
            if right > cur:
                cur = right
                yield cur
            try:
                right = next(iter_two)
            except StopIteration:
                last = left
                break
    if last > cur:
        yield last
    for i in iter_one:
        yield i
