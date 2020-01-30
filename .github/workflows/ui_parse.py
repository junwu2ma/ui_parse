import json
import string
import sys

def find_in_tree(pred, subtree):
    result = []
    #if pred(subtree):
    #    result = [subtree] 
    for subview in subtree.get("subviews", []): 
        if pred(subview):
            result += [subview] 
        if len(subview.get("contentView", [])) > 0 :
            subview = subview.get("contentView", [])
        elif len(subview.get("control", [])) > 0 : #not sure this is the right way to handle. but from the data, looks like "control" does not have subviews.
            subview = subview.get("control", [])
            if pred(subview):
                result += [subview] 
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
    # run like "ui_parse systemviewcontroller.json"

    if len(sys.argv) != 2:
        #sys.stderr.write("Enter json file name (Default=systemviewcontroller.json):\n".format(sys.argv[0]))
        #sys.stderr.write("usage: {} [PATH-TO-JSON]\n".format(sys.argv[0]))
        #sys.exit(1)   
        jsonfile = "systemviewcontroller.json" #hardcode the file name. just copy the file to the same folder as this
        try:               
            with open(jsonfile) as f:
                tree = json.load(f)                   
        except :
            sys.stderr.write("File read error or file does not exist (default: systemviewcontroller.json) ")
            exit(1)
     
    while True:
        sys.stderr.write("\nEnter selector (class, .classname,#identifier): ")   #waiting for selector.  
        sel = parse_selector(input())
        candidates = [tree]
        while len(sel) > 0:
            pred = build_compound_predicate(sel.pop(0))
#            print(pred)
            tmp = candidates
            candidates = []
            for candidate in tmp:                
            
                candidates += find_in_tree(pred, candidate)
        print(json.dumps(candidates))
        print("total records found: " + str(len(candidates)))   
         
         
