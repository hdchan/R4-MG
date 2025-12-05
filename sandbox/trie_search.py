import json
from typing import Optional, List

class Trie:
    def __init__(self, value: str = ""):
        self.value = value
        self.search_results = []
        self.children = []

    def has_child(self, value: str) -> Optional['Trie']:
        for c in self.children:
            if c.value == value:
                return c
        return None

    def add_child(self, value: str) -> 'Trie':
        result = Trie(value)
        self.children.append(result)
        return result

root = Trie()

with open('sandbox/sor.json', 'r') as file:
    data = json.load(file)
    for d in data['data']:
        # print(d['Name'])
        filtered_string = "".join(filter(str.isalnum, d['Name']))
        string_string = filtered_string.lower()
        array_string = list(string_string)

        for i in range(len(array_string)):
            curr_array_string = array_string[i:len(array_string)]
            curr = root
            for idx, c in enumerate(curr_array_string):
                found_child = curr.has_child(c)
                if found_child is None:
                    curr = curr.add_child(c)
                else:
                    curr = found_child
                if idx == len(curr_array_string) - 1:
                    curr.search_results.append(string_string)


def search(term: str) -> List[str]:
    array_string = list(term)
    curr_root = root
    for idx, c in enumerate(array_string):
        next_root = curr_root.has_child(c)
        if next_root is not None:
            curr_root = next_root
            continue
        else:
            return ["No results"]

    results = []
    stack = [curr_root]
    while len(stack) > 0:
        curr = stack.pop()
        stack += curr.children
        results += curr.search_results
    return results

result = search("at")

print(result)