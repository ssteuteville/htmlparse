#!/usr/bin/python3.2
import re
import tokens as tk
from state_machine import StateMachine, ParseError
__author__ = 'shane'
tokens =[]
buffer = ""
markup_parse = False


class State(object):
    def run(self):
        raise NotImplementedError("Subclasses of state should define a run method")
    def next(self, input):
        raise NotImplementedError("Subclasses of state should define a next method")


class AfterAttributeValueQuote(State):
    def run(self):
        print("After Quoted Attribute Value")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BeforeAttributeName
        #elif input=="/":
        #    return HtmlTokenizer.SelfClosingStartTag
        elif input == ">":
            return HtmlTokenizer.Data
        #elif EOF #TODO
        else:
            self.current_state = HtmlTokenizer.Data
            self.current_state.run()
            raise ParseError("Parse Error After Attribute Value", state_change=self.current_state.next(input))

class AttributeName(State):
    def run(self):
        print("Attribute Name")

    def next(self, input):
        invalid = ['"', "'", "<", "="]
        if input.isspace():
            return HtmlTokenizer.AfterAttributeName
        #elif input=="/":
        #    return HtmlTokenizer.SelfClosingTag
        elif input=="=":
            return HtmlTokenizer.BeforeAttributeValue
        elif input==">":
            return HtmlTokenizer.Data
        elif re.match(r"[A-Z]]", input):
            tokens[-1].attributes[-1][0] += input
            return HtmlTokenizer.AttributeName
        #elif input == None: #TODO Parse error. Append a U+FFFD REPLACEMENT CHARACTER character to the current attribute's name
        elif input in invalid:
            tokens[-1].attributes[-1][0] += input
            raise ParseError("Invalid attribute char", state_change=HtmlTokenizer.AttributeName)
        #elif EOF
            #TODO Parse error. Switch to the data state. Reconsume the EOF character.
        else:
            tokens[-1].attributes[-1][0] += input
            return HtmlTokenizer.AttributeName

class AttributeValueDoubleQuote(State):
    def run(self):
        print("Attribute Value Double Quote")

    def next(self, input):
        print(input)
        if input == '"':
            print("made it")
            return HtmlTokenizer.AfterAttributeValueQuote
        #elif input=="&": #TODO
        #    return CharacterReferenceInAttributeValue
        #elif input == None: #TODO
        else:
            tokens[-1].attributes[-1][1] += input
            return HtmlTokenizer.AttributeValueDoubleQuote


class BeforeAttributeName(State):
    def run(self):
        print("Before Attribute Name")

    def next(self, input):
        invalid = ['"', "'", "<", "="]
        if input.isspace():
            return HtmlTokenizer.BeforeAttributName
        #elif input == "/": #TODO
        #    return HtmlTokenizer.SelfClosingStartTag
        elif input == ">":
            return HtmlTokenizer.Data
        elif re.match(r'[A-Z]', input):
            tokens[-1].attributes.append([input.lower(), ""])
        #elif input == None: #TODO
        #    tokens[-1].attributes.append(u"\uFFFD", "")
        elif input in invalid:
            tokens[-1].attributes.append([input.lower(), ""])
            raise ParseError("Parse error invalid character in attribute name", state_change=HtmlTokenizer.AttributeName)
        #elif EOF #TODO
        else:
            tokens[-1].attributes.append([input,""])
            return HtmlTokenizer.AttributeName

class BeforeAttributeValue(State):
    def run(self):
        print("Before Attribute Value State")

    def next(self, input):
        invalid = ["<", "=", "`"]
        if input.isspace():
            return HtmlTokenizer.BeforeAttributeValue
        elif input == '"':
            return HtmlTokenizer.AttributeValueDoubleQuote
        #elif input == '"':#TODO
        #    return HtmlTokenizer.AttributeValueSingleQuote
        #elif input == "&":#TODO
        #    return HtmlTokenizer.AttributeValueNoQuote
        #elif input == None:
            #TODO Parse error. Append a U+FFFD REPLACEMENT CHARACTER character to the current attribute's value. Switch to the attribute value (unquoted) state.
        elif input==">":
            raise ParseError("invalid attribute value char", state_change=HtmlTokenizer.Data)
        #elif input in invalid:#TODO
        #    raise ParseError("Invalid Attribut Value Char, but allowed", state_change=HtmlTokenizer.AttributeValueNoQuote)
        #else:#TODO
        #    return HtmlTokenizer.AttributeValueNoQuote



class CharacterReferenceData(State):
    def run(self):
        raise NotImplementedError("Not implemented yet.")
    def next(self, input):
        raise NotImplementedError("Not implemented yet.")

class Data(State):
    def run(self):
        print("Data State")

    def next(self, input):
        if input == '<':
            return HtmlTokenizer.TagOpen
        elif input == "&":
            tokens.append(tk.Character(input))
            raise ParseError("Ignoring Character References For Now", state_change=HtmlTokenizer.Data)
            #return HtmlTokenizer.CharacterReferenceDataState
        else:
            tokens.append(tk.Character(input))
            return HtmlTokenizer.Data

class EndTagOpen(State):
    def run(self):
        print("End Tag Open")

    def next(self, input):
        if re.match(r'[a-z]', input):
            tokens.append(tk.StopTag(input))
            return HtmlTokenizer.TagName
        elif re.match(r'[A-Z]', input):
            tokens.append(tk.StopTag(input.lower()))
            return HtmlTokenizer.TagName
        elif input ==">":
            raise ParseError("Parsing Error Stop Tag Open incorrect '>'", state_change=HtmlTokenizer.Data)
        else:
            raise ParseError("Invalid open stop open tag", state_change=HtmlTokenizer.Data)

#class MarkupDeclarationOpen(State):
#    def run(self):
#        print("Markup Declaration Open")
#
#    def next(self, input):
#        global buffer, markup_parse
#        buffer += input
#        if buffer not in  "--" and buffer != "DOCTYPE" and buffer != "doctype" and buffer != "[CDATA[":
#            markup_parse = True
#
#        if markup_parse:
#            if buffer == '--':
#                tokens.append(tk.Comment())
#                markup_parse = False
#                buffer = ""
#                return HtmlTokenizer.CommentStartState
#            elif re.match(buffer, r"doctype", re.IGNORECASE):
#                markup_parse = False
#                buffer = ""
#                return HtmlTokenizer.DOCTYPE
#            elif buffer == "[CDATA[":
#                markup_parse = False
#                buffer = ""
#                return HtmlTokenizer.CDATASection
#        else:
#            return HtmlTokenizer.BogusComment




class TagName(State):
    def run(self):
        print("Tag name state")

    def next(self, input):
        if re.match(r'[a-z]', input):
            tokens[-1].tag_name += input
            return HtmlTokenizer.TagName
        elif input == ">":
            return HtmlTokenizer.Data
        elif input.isspace():
            return HtmlTokenizer.BeforeAttributeName
        #elif input == "/":                         #TODO http://www.w3.org/TR/html5/syntax.html#tag-name-state
        #    return HtmlTokenizer.SelfClosingStartTag
        elif re.match(r'[A-Z]', input):
            tokens[-1].tag_name += input.lower()
            return HtmlTokenizer.TagName
        else:
            return HtmlTokenizer.Data

class TagOpen(State):
    def run(self):
        print("Tag Open State")

    def next(self, input):
        global tokens
        if re.match(r'[a-z]', input):
            tokens.append(tk.StartTag(input))
            return HtmlTokenizer.TagName
        elif input == "/":
            return HtmlTokenizer.EndTagOpen
        #elif input == "!":#TODO
        #    global markup_parse#TODO
        #    markup_parse = True#TODO
        #    return HtmlTokenizer.MarkupDeclarationOpen#TODO
        #elif input == "?":#TODO
        #    raise ParseError("Parsing Error bogus comment Stop Tag Open", state_change=HtmlTokenizer.BogusComment)#TODO
        else:
            self.current_state = HtmlTokenizer.Data
            self.current_state.run()
            raise ParseError("Parse Error open tag didn't match syntax.",state_change=self.current_state.next(input))





class HtmlTokenizer(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, HtmlTokenizer.Data)


HtmlTokenizer.Data = Data()
HtmlTokenizer.TagOpen = TagOpen()
HtmlTokenizer.TagName = TagName()
HtmlTokenizer.EndTagOpen = EndTagOpen()
HtmlTokenizer.CurrentReferenceData = CharacterReferenceData() #TODO
HtmlTokenizer.BeforeAttributeName = BeforeAttributeName()
HtmlTokenizer.AttributeName = AttributeName()
HtmlTokenizer.AttributeValueDoubleQuote = AttributeValueDoubleQuote()
HtmlTokenizer.AfterAttributeValueQuote = AfterAttributeValueQuote()
HtmlTokenizer.BeforeAttributeValue = BeforeAttributeValue()
#HtmlTokenizer.MarkupDeclarationOpen = MarkupDeclarationOpen() #TODO
#HtmlTokenizer.BogusComment = BogusComment() #TODO
#HtmlTokenizer.CommentStartDash = CommentStartDash() #TODO


if __name__ == "__main__":
    print("hello")
    HtmlTokenizer().run_all('<head attr="attr"> <body test="test"> asoikjd&2312<? </body> </Head>')
    print(tokens[0].attributes)
    print(tokens[2].attributes)
    for token in tokens:
        if isinstance(token, tk.StartTag) or isinstance(token, tk.StopTag):
            print(token.tag_name + "  ---------> " + str(type(token)))
        elif isinstance(token, tk.Character):
            print(token.data + "  ---------> " + str(type(token)))



