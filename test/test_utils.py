import utils

def test_jacard():
    """Manually calculating jacard and comparing with results of function"""
    word = {'w', 'o', 'r', 'd', '$', '$w', 'wo', 'or', 'rd', 'd$', '$wo',
            'wor', 'ord', 'rd$'}
    ward = {'w', 'a', 'r', 'd', '$', '$w', 'wa', 'ar', 'rd', 'd$', '$wa',
            'war', 'ard', 'rd$'}
    # Manual calculation
    intersec = 8
    w_gram = 14
    a_gram = 14
    ans = intersec / (14 + 14 - intersec)
    assert utils.calculate_jacard_coeff(word, ward) == ans

def test_edit_dist():
    """Checking edit distance between two words"""
    word = "word"
    other = "wart"
    assert utils.edit_dist(word, other) == 2

def test_list_intersection():
    """Testing that list intersection handles basic lists"""
    list_one = [1, 3, 5, 7, 9]
    list_two = [2, 4, 5, 6]
    assert list(utils.intersect_sorted_lists(list_one, list_two)) == [5]

def test_first_list_short_intersection():
    """Testing that list intersection handles when first list shorter"""
    list_one = [1, 2]
    list_two = [2, 4, 5, 6]
    assert list(utils.intersect_sorted_lists(list_one, list_two)) == [2]

def test_list_intersection_empty():
    """Testing that list intersection handles one empty list"""
    list_one = [1, 3, 5, 7, 9]
    list_two = []
    assert list(utils.intersect_sorted_lists(list_one, list_two)) == []

def test_list_union():
    """Testing that list union handles basic lists"""
    list_one = [1, 3, 5, 7, 9]
    list_two = [2, 4, 5, 6]
    assert list(utils.union_sorted_lists(list_one, list_two)) == [1, 2, 3, 4, 5, 6, 7, 9]

def test_first_list_short_union():
    """Testing that list union handles when first list shorter"""
    list_one = [1, 2]
    list_two = [2, 4, 5, 6]
    assert list(utils.union_sorted_lists(list_one, list_two)) == [1, 2, 4, 5, 6]

def test_list_union_empty():
    """Testing that list union handles one empty list"""
    list_one = [1, 3, 5, 7, 9]
    list_two = []
    assert list(utils.union_sorted_lists(list_one, list_two)) == list_one
