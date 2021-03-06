from Token import Token
from util import center


class Variable(Token):
    def __init__(self, name, value=True):
        super().__init__()
        self.name = name
        self.value = value

    def calculate_value(self):
        return self.value

    def get_truth_table_header(self, depth):
        return center(self.name, len(self.name), depth=depth)

    def get_truth_table_entry(self, depth):
        return center(self.value, len(self.name), depth=depth)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.name == other.name
        return False

    def __gt__(self, other):
        return self.name > (other.name if isinstance(other, Variable) else other.children[0].name)

    def __hash__(self):
        return hash(self.name)

    def clone(self):
        return Variable(self.name, self.value)


TRUE = Variable("true", True)
FALSE = Variable("false", False)
