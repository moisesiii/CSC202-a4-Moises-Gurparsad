from typing import *
from dataclasses import dataclass
import unittest
import sys
import string
sys.setrecursionlimit(10**6)
IntList : TypeAlias = Optional['ILNode']

WordLinesList : TypeAlias = Optional['WordLines']



@dataclass(frozen=True)
class ILNode:
    first : int
    rest  : IntList

@dataclass
class WordLines:
    key : str
    value : IntList
    rest : WordLinesList = None

@dataclass
class Hash:
    array : list[WordLinesList]
    count : int

HashTable : TypeAlias = Hash



# Return the hash code of 's' (see assignment description).
def hash_fn(s: str) -> int:
    total = 0 
    for ch in s: 
        total = total * 31 + ord(ch)
    return total
    

# Make a fresh hash table with the given number of bins 'size',
# containing no elements.
def make_hash(size: int) -> HashTable:
    return Hash([None] * size,0)
    

# Return the number of bins in 'ht'.
def hash_size(ht: HashTable) -> int:
    return len(ht.array)
    

# Return the number of elements (key-value pairs) in 'ht'.
def hash_count(ht: HashTable) -> int:
    return ht.count
    

# Return whether 'ht' contains a mapping for the given 'word'.
def has_key_in_list(wlst: WordLinesList, word: str) -> bool:
    if wlst is None:
        return False
    elif wlst.key == word:
        return True
    else:
        return has_key_in_list(wlst.rest, word) 
def has_key(ht: HashTable, word: str) -> bool:
    index = hash_fn(word) % hash_size(ht)
    return has_key_in_list(ht.array[index], word)
    



# Gurparsad (this half) ------------------------------------------------------------------------

# Return the line numbers associated with the key 'word' in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def lookup(ht: HashTable, word: str) -> List[int]:
    # bin_idx = hash num % # of bins
    bin_idx = hash_fn(word) % hash_size(ht) 
    current = ht.array[bin_idx]  # the current node
    
    while current is not None:
        if current.key == word:
            return lookup_helper(current.value)
        current = current.rest
    return []

# Converts 'nums' to a simple array of integers.
def lookup_helper(nums: IntList) -> List[int]:
    result = []

    while nums is not None:
        result.append(nums.first)
        nums = nums.rest
    return result
    

# Record in 'ht' that 'word' has an occurrence on line 'line'.
def add(ht: HashTable, word: str, line: int) -> None:
    bin_idx = hash_fn(word) % hash_size(ht)
    current = ht.array[bin_idx]

    while current is not None:
        if current.key == word:
            if not intlist_contains(current.value, line):
                current.value = ILNode(line, current.value)
            return

        current = current.rest

    new_node = WordLines(word, ILNode(line, None), ht.array[bin_idx])
    ht.array[bin_idx] = new_node
    ht.count += 1

def intlist_contains(nums: IntList, line: int) -> bool:
    while nums is not None:
        if nums.first == line:
            return True
        nums = nums.rest
    return False

# Return the words that have mappings in 'ht'.
# The returned list should not contain duplicates, but need not be sorted.
def hash_keys(ht: HashTable) -> List[str]:
    result = []

    for bin in ht.array:
        current = bin

        while current is not None:
            result.append(current.key)
            current = current.rest

    return result

# Given a hash table 'stop_words' containing stop words as keys, plus
# a sequence of strings 'lines' representing the lines of a document,
# return a hash table representing a concordance of that document.
def make_concordance(stop_words: HashTable, lines: List[str]) -> HashTable:
    ht = make_hash(128)
    
    line_num = 1

    for line in lines: 
        line = line.replace("'", "")

        for punc in string.punctuation:
            line = line.replace(punc, " ")

        line = line.lower()

        words = line.split()

        for word in words:
            if word.isalpha() and not has_key(stop_words, word):
                add(ht, word, line_num)

        line_num += 1

    return ht

# Given an input file path, a stop-words file path, and an output file path,
# overwrite the indicated output file with a sorted concordance of the input file.
def full_concordance(in_file: str, stop_words_file: str, out_file: str) -> None:

    stop_words = make_hash(128)

    with open(stop_words_file, "r") as f:
        for line in f:
            word = line.strip().lower()

            if word != "":
                add(stop_words, word, 0)

    with open(in_file, "r") as f:
        lines = f.readlines()

    concordance = make_concordance(stop_words, lines)

    words = hash_keys(concordance)
    words.sort()

    with open(out_file, "w") as f:
        for word in words:
            nums = lookup(concordance, word)

            line = word + ": " + " ".join(str(n) for n in nums)

            f.write(line + "\n")


class Tests(unittest.TestCase):
    def test_lookup_missing(self):
        ht = make_hash(128)
        self.assertEqual(lookup(ht, "cat"), [])

    def test_add_lookup_one(self):
        ht = make_hash(128)
        add(ht, "cat", 3)
        self.assertEqual(lookup(ht, "cat"), [3])

    def test_add_no_duplicate_line(self):
        ht = make_hash(128)
        add(ht, "cat", 3)
        add(ht, "cat", 3)
        self.assertEqual(lookup(ht, "cat"), [3])

    def test_hash_keys(self):
        ht = make_hash(128)
        add(ht, "cat", 1)
        add(ht, "dog", 2)
        self.assertEqual(sorted(hash_keys(ht)), ["cat", "dog"])

    def test_make_concordance(self):
        stop = make_hash(128)
        add(stop, "the", 0)

        lines = ["The cat, cat!", "Dog's cat"]
        ht = make_concordance(stop, lines)

        self.assertEqual(sorted(lookup(ht, "cat")), [1, 2])
        self.assertEqual(lookup(ht, "dogs"), [2])
        self.assertEqual(lookup(ht, "the"), [])
    
    def test_hash_fn_empty(self): 
        self.assertEqual(hash_fn(""),0) 
    def test_hash_fn_one_letter(self):
        self.assertEqual(hash_fn("a"), ord("a")) 
    
    def test_hash_fn_word(self):
        self.assertEqual(
            hash_fn("cat"),
            ord("c") * 31 * 31 + ord("a") * 31 + ord("t")
        ) 

    def test_make_hash(self):
        ht = make_hash(5)
        self.assertEqual(ht.array, [None, None, None, None, None])
        self.assertEqual(ht.count, 0)
    def test_hash_size(self):
        ht = make_hash(7)
        self.assertEqual(hash_size(ht), 7) 
    def test_hash_count_empty(self):
        ht = make_hash(7)
        self.assertEqual(hash_count(ht), 0)
    def test_hash_count_nonzero(self):
        ht = make_hash(7)
        ht.count = 3
        self.assertEqual(hash_count(ht), 3)

    def test_has_key_empty(self):
        ht = make_hash(10)

        self.assertFalse(has_key(ht, "cat"))

    def test_has_key_present(self):
        ht = make_hash(10)

        index = hash_fn("cat") % hash_size(ht)
        ht.array[index] = WordLines("cat", ILNode(1, None))
        ht.count = 1

        self.assertTrue(has_key(ht, "cat"))

    def test_has_key_missing(self):
        ht = make_hash(10)

        index = hash_fn("cat") % hash_size(ht)
        ht.array[index] = WordLines("cat", ILNode(1, None))
        ht.count = 1

        self.assertFalse(has_key(ht, "dog"))

    def test_has_key_in_chain(self):
        ht = make_hash(1)

        ht.array[0] = WordLines(
            "cat",
            ILNode(1, None),
            WordLines("dog", ILNode(2, None))
        )
        ht.count = 2

        self.assertTrue(has_key(ht, "cat"))
        self.assertTrue(has_key(ht, "dog"))
        self.assertFalse(has_key(ht, "fish"))   


if (__name__ == '__main__'):
    unittest.main()
