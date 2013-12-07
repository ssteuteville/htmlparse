#!/usr/bin/python3.2
__author__ = 'shane'
#from exceptions import BaseException


class ParseError(BaseException):
    def __init__(self, message,token_change=None, state_change=None):
        # Call the base class constructor with the parameters it needs
        BaseException.__init__(self, message)
        # Now for your custom code...
        self.message = message
        self.token_change = token_change
        self.state_change = state_change

class StateMachine(object):
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_state.run()

    def run_all(self, inputs):
        for input in inputs:
            try:
                self.current_state = self.current_state.next(input)
            except ParseError as e:
                print(e.message)
                if e.state_change:
                    self.current_state = e.state_change

            self.current_state.run()
