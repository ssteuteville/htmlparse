#!/usr/bin/python3.2
import re
import tokens as tk
import html_tree_constructor as tree
from state_machine import StateMachine, ParseError
__author__ = 'shane'
tokens =[] #treated as current element stack.
temp_buffer = ""
use_buffer = False


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
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #elif EOF #TODO
        else:
            self.current_state = HtmlTokenizer.Data
            self.current_state.run()
            raise ParseError("Parse Error After Attribute Value", state_change=self.current_state.next(input))

class AfterDOCTYPEName(State):
    def run(self):
        print("After DOCTYPE Name")

    def next(self, input):
        print("input = %s" % input)
        global temp_buffer
        if input.isspace():
            return HtmlTokenizer.AfterDOCTYPEName
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #TODO handle EOF case
        elif len(temp_buffer) <= 6:
            temp_buffer += input
            if temp_buffer.lower() == "public":
                temp_buffer = ""
                return HtmlTokenizer.AfterDOCTYPEPublicKeyword
            elif temp_buffer.lower() == "system":
                temp_buffer = ""
                return HtmlTokenizer.AfterDOCTYPESystemKeyword
            else:
                return HtmlTokenizer.AfterDOCTYPEName
        else:
            tokens[-1].force_quirks_flag = "on"
            return HtmlTokenizer.BogusDOCTYPE

class AfterDOCTYPEPublicIdentifier(State):
    def run(self):
        print("After DOCTYPE Public Identifier")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BetweenDOCTYPEPublicAndSystemIdentifier
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        elif input =='"':
            return HtmlTokenizer.DOCTYPESystemIdentifierDoubleQuote #TODO implement this state
        #TODO EOF and single quote
        #else: #TODO Implement BogusDOCTYPE
        #    tokens[-1].force_quirks_flag = "on"
        #    raise ParseError("Error After DOCTYPE Public Identifier", state_change=HtmlTokenizer.BogusDOCTYPE)

class AfterDOCTYPEPublicKeyword(State):
    def run(self):
        print("After DOCTYPE PUBLIC KEYWORD")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BeforeDOCTYPEPublicIdentifier
        elif input == '"':
            raise ParseError("After DOCTYPE Public Keyword", state_change=HtmlTokenizer.DOCTYPEPublicIdentifierDoubleQuote)
        #TODO single quote and eof cases
        elif input == ">":
            tokens[-1].force_quirks_flag = "on"
            HtmlTokenizer.tree.emit(tokens[-1])
            raise ParseError("After DOCTYPE Public Keyword", state_change=HtmlTokenizer.Data)
        #else:
        #    tokens[-1].force_quirks_flag = "on"
        #    raise ParseError("After DOCTYPE Public Keyword", state_change=HtmlTokenizer.BogusDOCTYPE)

class AfterDOCTYPESystemKeyword(State):
    def run(self):
        print("After DOCTYPE System Keyword")

    def next(self, input):
        print("input=%s" % input)
        if input.isspace():
            return HtmlTokenizer.BeforeDOCTYPESystemIdentifier
        elif input == '"':
            return HtmlTokenizer.DOCTYPESystemIdentifierDoubleQuote
        elif input ==">":
            tokens[-1].force_quirks_flag = "on"
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #TODO EOF and Single Quote Cases
        else:
            tokens[-1].force_quirks_flag = "on"
            raise ParseError("After DOCTYPE System Keyword ERROR", state_change=HtmlTokenizer.BogusDOCTYPE)

class AfterDOCTYPESystemIdentifier(State):
    def run(self):
        print("After DOCTYPE System ID State")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.AfterDOCTYPESystemIdentifier
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #TODO EOF Case
        else:
            raise ParseError("After DOCTYPE SYSTEM ID STATE ERROR", state_change=HtmlTokenizer.BogusDOCTYPE)

class BogusDOCTYPE(State):
    def run(self):
        print("BOGUS DOCTYPE STATE")

    def next(self, input):
        if input == ">":
            return HtmlTokenizer.Data
        #TODO EOF
        else:
            return HtmlTokenizer.BogusDOCTYPE


class AttributeName(State):
    def run(self):
        print("Attribute Name")

    def next(self, input):
        invalid = ['"', "'", "<", "="]
        if input.isspace():
            return HtmlTokenizer.AfterAttributeName
        #elif input=="/":#TODO
        #    return HtmlTokenizer.SelfClosingTag
        elif input=="=":
            return HtmlTokenizer.BeforeAttributeValue
        elif input==">":
            HtmlTokenizer.tree.emit(tokens[-1])
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
        if input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
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
            #TODO before this emit make sure that there aren't two attributes with the same name
            HtmlTokenizer.tree.emit(tokens[-1])
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
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            raise ParseError("Before attribute value ERROR", HtmlTokenizer.Data)
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
        else:
            return HtmlTokenizer.AttributeValueDoubleQuote

class BeforeDOCTYPEName(State):
    def run(self):
        print("Before DOCTYPE Name")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BeforeDOCTYPEName
        elif re.match(r'[A-Z]', input):
            tokens.append(tk.Doctype())
            tokens[-1].name = input.lower()
            return HtmlTokenizer.DOCTYPEName
        #TODO elif EOF or NULL
        elif input == ">":
            tokens.append(tk.Doctype())
            tokens[-1].force_quirks_flag = "on"
            HtmlTokenizer.tree.emit(tokens[-1])
            raise ParseError("BEFORE DOCTYPE NAME ERROR", state_change=HtmlTokenizer.Data)
        else:
            tokens.append(tk.Doctype())
            tokens[-1].name = input
            return HtmlTokenizer.DOCTYPEName

class BetweenDOCTYPEPublicAndSystemIdentifier(State):
    def run(self):
        print("Between DOCTYPE public and system Identifier")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BetweenDOCTYPEPublicAndSystemIdentifier
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        elif input == '"':
            tokens[-1].system_id = ""
            return HtmlTokenizer.DOCTYPESystemIdentifierDoubleQuote
        #TODO EOF
        else:
            print("input=%s" % input)
            raise ParseError("Between public and system DOCTYPE id", state_change=HtmlTokenizer.BogusDOCTYPE)

class BeforeDOCTYPEPublicIdentifier(State):
    def run(self):
        print("Before DOCTYPE Public ID")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BeforeDOCTYPEPublicIdentifier
        elif input == '"':
            tokens[-1].public_id = ""
            return HtmlTokenizer.DOCTYPEPublicIdentifierDoubleQuote
        #TODO Single quote case
        elif input == ">":
            tokens[-1].force_quirks_flag = "on"
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #TODO EOF CASE
        else:
            tokens[-1].force_quirks_flag = "on"
            raise ParseError("BEFORE DOCTYPE PUB ID ERROR", state_change=HtmlTokenizer.BogusDOCTYPE)

class BeforeDOCTYPESystemIdentifier(State):
    def run(self):
        print("Before Doctype System Id STATE")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BeforeDOCTYPESystemIdentifier
        elif input =='"':
            tokens[-1].system_id = ""
            return HtmlTokenizer.DOCTYPESystemIdentifierDoubleQuote
        elif input == ">":
            tokens[-1].force_quirks_flag = "on"
            return HtmlTokenizer.Data
        #TODO EOF
        else:
            tokens[-1].force_quirks_flag = "on"
            return HtmlTokenizer.BogusDOCTYPE

class BogusComment(State):
    def run(self):
        print("Bogus Comment")

    def next(self, input):
        global temp_buffer
        if input != ">":
            temp_buffer += input
            return HtmlTokenizer.BogusComment
        #TODO EOF CASE
        else:
            bogusComment = tk.Comment()
            bogusComment.data = temp_buffer
            temp_buffer = ""
            tokens.append(bogusComment)
            return HtmlTokenizer.Data




class Comment(State):
    def run(self):
        print("Comment State")

    def next(self, input):
        if input == "-":
            return HtmlTokenizer.CommentEndDash
        #elif input == None:
            #todo parse error add replacement char to data
        #todo elif EOF case
        else:
            tokens[-1].data += input
            return HtmlTokenizer.Comment

class CommentEnd(State):
    def run(self):
        print("Comment End State")

    def next(self, input):
        if input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        elif input=="!":
            raise ParseError("Comment End State", next_state=HtmlTokenizer.CommentEndBang)
        elif input =="-":
            tokens[-1] += "-"
            raise ParseError("Comment End State" ,HtmlTokenizer.current_state)
        #TODO EOF and NULL cases
        else:
            tokens[-1] += "--"
            raise ParseError("Comment End State", HtmlTokenizer.Comment)

class CommentEndBang(State):
    def run(self):
        print("Comment End Bang State")

    def next(self, input):
        if input == "-":
            tokens[-1] += "--"
            return HtmlTokenizer.CommentEndDash
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #TODO NULL and EOF
        else:
            tokens[-1] += ("--"+input)
            return HtmlTokenizer.Comment

class CommentEndDash(State):
    def run(self):
        print("Commend End Dash State")

    def next(self, input):
        if input == "-":
            return HtmlTokenizer.CommentEnd
        #elif #TODO null and EOF cases
        else:
            tokens[-1] += input
            return HtmlTokenizer.Comment

class CommentStart(State):
    def run(self):
        print("Comment Start State")

    def next(self, input):
        if input == "-":
            return HtmlTokenizer.CommentStartDash
        #elif input == None:
            #add replacement char to comment.data
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        else:#todo handle EOF case
            tokens[-1].data += input
            return HtmlTokenizer.Comment

class CommentStartDash(State):
    def run(self):
        print("Comment Start Dash")

    def next(self, input):
        if input == "-":
            return HtmlTokenizer.CommentEnd
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        #TODO EOF and NULL
        else:
            tokens[-1] += ("-"+input)
            return HtmlTokenizer.Comment

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
            HtmlTokenizer.tree.emit(tk.Character(input))
            return HtmlTokenizer.Data
class DOCTYPE(State):
    def run(self):
        print("DOCTYPE STATE")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.BeforeDOCTYPEName
        #TODO elif EOF
        else:
            return HtmlTokenizer.BeforeDOCTYPEName.next(input)
            #TODO this should be raise a parse error but I havent figured out how to reconsume char and parse error

class DOCTYPEName(State):
    def run(self):
        print("DOCTYPE Name State")

    def next(self, input):
        if input.isspace():
            return HtmlTokenizer.AfterDOCTYPEName
        elif input==">":
            HtmlTokenizer.tree.emit(tokens[-1])
            return HtmlTokenizer.Data
        elif re.match(r'[A-Z]', input):
            tokens[-1].name += input.lower()
            return HtmlTokenizer.DOCTYPEName
        #todo elif EOF NULL
        else:
            tokens[-1].name += input
            return HtmlTokenizer.DOCTYPEName

class DOCTYPEPublicIdentifierDoubleQuote(State):
    def run(self):
        print("DOCTYPE Public Identifier Double Quoted")

    def next(self, input):
        if input == '"':
            return HtmlTokenizer.AfterDOCTYPEPublicIdentifier
        elif input == ">":
            tokens[-1].force_quirks_flag = "on"
            HtmlTokenizer.tree.emit(tokens[-1])
            raise ParseError("Public Identifier Double Quoted Error", state_change=HtmlTokenizer.Data)
        #TODO cases for EOF and NULL
        else:
            tokens[-1].public_id += input
            return HtmlTokenizer.DOCTYPEPublicIdentifierDoubleQuote

class DOCTYPESystemIdentifierDoubleQuote(State):
    def run(self):
        print("DOCTYPE System Identifier")

    def next(self, input):
        if input == '"':
            return HtmlTokenizer.AfterDOCTYPESystemIdentifier
        elif input == ">":
            tokens[-1].force_quirks_flag = "on"
            HtmlTokenizer.tree.emit(tokens[-1])
            raise ParseError("DOCTYPE System ID ERROR", HtmlTokenizer.Data)
        #TODO NULL and EOF
        else:
            tokens[-1].system_id += input
            return HtmlTokenizer.DOCTYPESystemIdentifierDoubleQuote


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
        elif input ==">": #TODO emite "<" on EOF
            raise ParseError("Parsing Error Stop Tag Open incorrect '>'", state_change=HtmlTokenizer.Data)
        else:
            raise ParseError("Invalid open stop open tag", state_change=HtmlTokenizer.Data)

class MarkupDeclarationOpen(State):
    def run(self):
        print("Markup Declaration Open")

    def next(self, input):
        global temp_buffer
        global use_buffer
        temp_buffer += input
        if temp_buffer not in  "--" and temp_buffer not in "DOCTYPE" and temp_buffer not in "doctype" and temp_buffer not in"[CDATA[":
            use_buffer = False
        print("*" * 50)
        print("buffer = " + temp_buffer)
        print("*" * 50);
        if use_buffer:
            print("Use Buffer.")
            if temp_buffer == '--':
                tokens.append(tk.Comment())
                tokens.append(tk.Comment())
                use_buffer = False
                temp_buffer = ""
                return HtmlTokenizer.CommentStart
            elif temp_buffer.lower() == "doctype":
                print("buffer was %s when it matched doctype" % temp_buffer)
                use_buffer = False
                temp_buffer = ""
                return HtmlTokenizer.DOCTYPE
        #    elif buffer == "[CDATA[":
        #        markup_parse = False
        #        buffer = ""
        #        return HtmlTokenizer.CDATASection
            elif len(temp_buffer) >6:
                global use_buffer
                use_buffer = False
                temp_buffer = ""
                return HtmlTokenizer.MarkupDeclarationOpen.next(input)
            else:
                return HtmlTokenizer.MarkupDeclarationOpen
        else:
            return HtmlTokenizer.BogusComment





class TagName(State):
    def run(self):
        print("Tag name state")

    def next(self, input):
        if re.match(r'[a-z]', input):
            tokens[-1].tag_name += input
            return HtmlTokenizer.TagName
        elif input == ">":
            HtmlTokenizer.tree.emit(tokens[-1])
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
        elif input == "!":#TODO
            global use_buffer#TODO
            use_buffer = True#TODO
            return HtmlTokenizer.MarkupDeclarationOpen#TODO
        #elif input == "?":#TODO
        #    raise ParseError("Parsing Error bogus comment Stop Tag Open", state_change=HtmlTokenizer.BogusComment)#TODO
        else:
            HtmlTokenizer.tree.emit(tk.Character('/'))
            self.current_state = HtmlTokenizer.Data
            self.current_state.run()
            raise ParseError("Parse Error open tag didn't match syntax.",state_change=self.current_state.next(input))





class HtmlTokenizer(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, HtmlTokenizer.Data)
HtmlTokenizer.AfterDOCTYPEPublicIdentifier = AfterDOCTYPEPublicIdentifier()
HtmlTokenizer.AfterDOCTYPEPublicKeyword = AfterDOCTYPEPublicKeyword()
HtmlTokenizer.AfterDOCTYPESystemKeyword = AfterDOCTYPESystemKeyword()
HtmlTokenizer.AfterDOCTYPESystemIdentifier = AfterDOCTYPESystemIdentifier()
HtmlTokenizer.BogusComment = BogusComment()
HtmlTokenizer.BeforeDOCTYPEPublicIdentifier = BeforeDOCTYPEPublicIdentifier()
HtmlTokenizer.BeforeDOCTYPESystemIdentifier = BeforeDOCTYPESystemIdentifier()
HtmlTokenizer.BetweenDOCTYPEPublicAndSystemIdentifier = BetweenDOCTYPEPublicAndSystemIdentifier()
HtmlTokenizer.Comment = Comment()
HtmlTokenizer.CommentEnd = CommentEnd()
HtmlTokenizer.CommentEndDash = CommentEndDash()
HtmlTokenizer.CommentStart = CommentStart()
HtmlTokenizer.CommentStartDash = CommentStartDash()
HtmlTokenizer.Data = Data()
HtmlTokenizer.DOCTYPE = DOCTYPE()
HtmlTokenizer.DOCTYPEPublicIdentifierDoubleQuote = DOCTYPEPublicIdentifierDoubleQuote()
HtmlTokenizer.DOCTYPESystemIdentifierDoubleQuote = DOCTYPESystemIdentifierDoubleQuote()
HtmlTokenizer.BeforeDOCTYPEName = BeforeDOCTYPEName()
HtmlTokenizer.DOCTYPEName = DOCTYPEName()
HtmlTokenizer.AfterDOCTYPEName = AfterDOCTYPEName()
HtmlTokenizer.BogusDOCTYPE = BogusDOCTYPE()
HtmlTokenizer.TagOpen = TagOpen()
HtmlTokenizer.TagName = TagName()
HtmlTokenizer.EndTagOpen = EndTagOpen()
HtmlTokenizer.CurrentReferenceData = CharacterReferenceData() #TODO
HtmlTokenizer.BeforeAttributeName = BeforeAttributeName()
HtmlTokenizer.AttributeName = AttributeName()
HtmlTokenizer.AttributeValueDoubleQuote = AttributeValueDoubleQuote()
HtmlTokenizer.AfterAttributeValueQuote = AfterAttributeValueQuote()
HtmlTokenizer.BeforeAttributeValue = BeforeAttributeValue()
HtmlTokenizer.tree = tree.HtmlTreeConstructor()
HtmlTokenizer.MarkupDeclarationOpen = MarkupDeclarationOpen() #TODO
#HtmlTokenizer.BogusComment = BogusComment() #TODO
#HtmlTokenizer.CommentStartDash = CommentStartDash() #TODO


if __name__ == "__main__":
    print("hello")
    HtmlTokenizer().run_all('<!DOCTYPE html public "harry" "cherry"><head attr1="attr1" attr2="attr2><!--Comment Text --></Head><body test="test"><div> body<? </div></body>')
    HtmlTokenizer.tree.print_tree()



