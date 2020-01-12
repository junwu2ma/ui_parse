import json
import string
import sys

def find_in_tree(pred, subtree):
    result = []
    if pred(subtree):
        result = [subtree]
    for subview in subtree.get("subviews", []):
        result += find_in_tree(pred, subview)
    return result

def class_predicate(name):
    return lambda s: "class" in s and s.get("class") == name

def class_name_predicate(name):
    return lambda s: "classNames" in s and name in s.get("classNames")

def identifier_predicate(name):
    return lambda s: "identifier" in s and s.get("identifier") == name

def whitespace(s):
    return all([c in string.whitespace for c in s])

def parse_compound(s):
    result = []
    while len(s) > 0:
        c = s[1:].find(".")
        i = s[1:].find("#")
        if c == -1 and i == -1:
            result.append(s)
            return result

        if c == -1:
            split = i
        elif i == -1:
            split = c
        else:
            split = min(c, i) 
        result.append(s[:split+1])
        s = s[split+1:]
    return result

def parse_selector(selector):
    chain = filter(lambda s: not whitespace(s), selector.split(" "))
    return list(map(parse_compound, chain))

def build_compound_predicate(components):
    predicates = []
    for component in components:
        if component.startswith("."):
            predicates.append(class_name_predicate(component[1:]))
        elif component.startswith("#"):
            predicates.append(identifier_predicate(component[1:]))
        else:
            predicates.append(class_predicate(component))
    return lambda s: all([p(s) for p in predicates])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("usage: {} [PATH-TO-JSON]\n".format(sys.argv[0]))
        sys.exit(1)
    with open(sys.argv[1]) as f:
        tree = json.load(f)
    while True:
        sel = parse_selector(input())
        candidates = [tree]
        while len(sel) > 0:
            pred = build_compound_predicate(sel.pop(0))
            tmp = candidates
            candidates = []
            for candidate in tmp:
                candidates += find_in_tree(pred, candidate)
        print(json.dumps(candidates))
