#!/usr/bin/python3.2
__author__ = 'shane'
import tokens as tk

#this is a placeholder for now
class HtmlTreeConstructor(object):
    def __init__(self):
        self.insertion_mode = "initial"
        self.tree = []

    def emit(self, input):
        self.tree.append(input)

    def print_tree(self):
        count = 0
        data = False
        print("DATA FORMAT")
        for token in self.tree:
            print(str(type(token)))

        print("HTML FORMAT")
        for token in self.tree:
            if isinstance(token, tk.StopTag):
                count -= 1
                if data:
                    print("")
                    data = False
                print(" "*count +"</" + token.tag_name + ">")
            elif isinstance(token, tk.StartTag):
                if data:
                    print("")
                    data = False
                print(" "*count + "<" + token.tag_name, end="")
                count += 1
                if len(token.attributes) > 0:
                    for attribute in token.attributes:
                        print((" "*count +attribute[0] + "=" + '"'+attribute[0] + '"'), end="")
                print(">")
            elif isinstance(token, tk.Character):
                if not data:
                    print(" "*(count), end="")
                print(token.data, end="")
                data = True
            elif isinstance(token, tk.Comment):
                print(" "*(count+1) + "<!--" + token.data + "-->")