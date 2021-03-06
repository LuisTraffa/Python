from abc import ABC

from Token import Token
from Variable import FALSE, TRUE, Variable
from constants import operators
from util import center


def get_operator(operator_name, children):
    return operator_classes[operator_name](children)


def get_operator_symbol(operator):
    res = "?"
    current_cls = None
    for symbol, cls in operator_classes.items():
        if isinstance(operator, cls):
            if not current_cls or issubclass(cls, current_cls):
                current_cls = cls
                res = symbol
    return res


class Operator(Token, ABC):
    def __init__(self, *children):
        super().__init__()
        if isinstance(children[0], list):
            self.children = children[0]
        else:
            self.children = list(children)

    def unary_traverse(self, operator):
        return operator + str(self.children[0])

    def multiple_traverse(self, operator):
        return "(" + (" " + operator + " ").join(map(str, self.children)) + ")"

    def get_truth_table_entry(self, depth):
        res = "("
        op_str = center(self.value, len(get_operator_symbol(self))+2, depth)
        for child in self.children:
            res += child.get_truth_table_entry(depth + 1)
            res += op_str
        res = res[:-len(op_str)]
        res += ")"
        return res

    def get_truth_table_header(self, depth):
        res = "("
        op_str = center(get_operator_symbol(self), len(get_operator_symbol(self))+2, depth)
        for child in self.children:
            res += child.get_truth_table_header(depth + 1)
            res += op_str
        res = res[:-len(op_str)]
        res += ")"
        return res

    def associative_law(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].associative_law()
        return self

    def absorption(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].absorption()
        return self

    def idempotence(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].idempotence()
        return self

    def trivial_simplification(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].trivial_simplification()
        return self

    def dominance(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].dominance()
        return self

    def identity(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].identity()
        return self

    def not_operator_simplify(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].not_operator_simplify()
        return self

    def replace_with_and_or(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].replace_with_and_or()
        return self

    def smart_expand(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].smart_expand()
        return self

    def smart_exclude(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].smart_exclude()
        return self

    def to_nand(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].replace_with_and_or().to_nand()
        return self

    def to_nor(self):
        for i in range(len(self.children)):
            self.children[i] = self.children[i].replace_with_and_or().to_nor()
        return self

    def clone(self):
        return self.__class__([child.clone for child in self.children])


class AndOrOperator(Operator, ABC):
    def associative_law(self):
        super().associative_law()

        if len(self.children) == 1:
            return self.children[0].associative_law()

        add_new = []
        rem = []
        for child in self.children:
            if isinstance(self, AndOperator) and isinstance(child, AndOperator) \
                    or isinstance(self, OrOperator) and isinstance(child, OrOperator):
                add_new.extend(child.children)
                rem.append(child)
        for it in rem:
            self.children.remove(it)
        self.children.extend(add_new)

        return self

    def absorption(self):
        super().absorption()

        rem = []
        for i in range(len(self.children)):
            if isinstance(self, OrOperator) and isinstance(self.children[i], AndOperator) or \
                    isinstance(self, AndOperator) and isinstance(self.children[i], OrOperator):
                for var in self.children:
                    if var in self.children[i].children:
                        rem.append(self.children[i])
        for it in rem:
            if it in self.children:
                self.children.remove(it)

        return self

    def smart_expand(self):
        super().smart_expand()

        if isinstance(self, OrOperator):
            child_operator = AndOperator
        else:
            child_operator = OrOperator

        rem = []
        for i in range(len(self.children)):
            if (isinstance(self, OrOperator) and isinstance(self.children[i], AndOperator) or
                    isinstance(self, AndOperator) and isinstance(self.children[i], OrOperator)):
                for var in self.children:
                    if isinstance(var, Variable) or isinstance(var, NotOperator):
                        new_children = []
                        for child in self.children[i].children:
                            new_children.append(self.__class__(var, child))
                        self.children[i] = child_operator(new_children)
                        rem.append(var)

        for it in rem:
            if it in self.children:
                self.children.remove(it)

        return self

    def smart_exclude_alt(self):
        super().smart_exclude()
        absolutely_new_children = []

        for i in range(len(self.children)):
            if isinstance(self, OrOperator) and isinstance(self.children[i], AndOperator) or \
                    isinstance(self, AndOperator) and isinstance(self.children[i], OrOperator):
                for j in range(len(self.children)):
                    if self.children[i] != self.children[j] and \
                            (isinstance(self.children[j], AndOperator) and isinstance(self.children[i], AndOperator) or
                             isinstance(self.children[j], OrOperator) and isinstance(self.children[i], OrOperator)):
                        intersection = [value for value in self.children[i].children if
                                        value in self.children[j].children]
                        if len(intersection) > 0:
                            for it in intersection:
                                self.children[i].children.remove(it)
                                self.children[j].children.remove(it)
                                absolutely_new_children.append(it)

        new_children = [child for child in self.children if isinstance(child, Variable) or len(child.children) != 0]
        new_children_2 = [child if isinstance(child, Variable) or len(child.children) != 1 else child.children[0]
                          for child in new_children]

        if len(absolutely_new_children) > 0:
            if isinstance(self, OrOperator):
                return AndOperator(*absolutely_new_children, OrOperator(new_children_2))
            else:
                return OrOperator(*absolutely_new_children, AndOperator(new_children_2))
        else:
            return self

    def smart_exclude(self):
        super().smart_exclude()

        if isinstance(self, OrOperator):
            outer_class = OrOperator
            inner_class = AndOperator
        else:
            outer_class = AndOperator
            inner_class = OrOperator

        if any(not isinstance(child, inner_class) for child in self.children):
            return self

        intersection = self.children[0].children
        for child in self.children:
            intersection = [elem for elem in intersection if elem in child.children]

        if len(intersection) == 0:
            return self

        for child in self.children:
            child.children = [elem for elem in child.children if elem not in intersection]

        self.children = [child if len(child.children) != 1 else child.children[0]
                         for child in self.children if len(child.children) > 0]
        return inner_class(*intersection, outer_class(self.children))

    def idempotence(self):
        super().idempotence()

        new_children = []
        for child in self.children:
            if child not in new_children:
                new_children.append(child)
        self.children = new_children

        if len(self.children) == 1:
            return self.children[0]

        return self

    def trivial_simplification(self):
        super().trivial_simplification()

        for child in self.children:
            if NotOperator(child) in self.children:
                if isinstance(self, OrOperator):
                    return TRUE
                else:
                    return FALSE

        return self

    def dominance(self):
        super().dominance()

        if isinstance(self, OrOperator) and TRUE in self.children:
            return TRUE
        elif isinstance(self, AndOperator) and FALSE in self.children:
            return FALSE

        return self

    def identity(self):
        super().identity()

        if isinstance(self, OrOperator):
            while FALSE in self.children and len(self.children) > 1:
                self.children.remove(FALSE)
        else:
            if isinstance(self, AndOperator):
                while TRUE in self.children and len(self.children) > 1:
                    self.children.remove(TRUE)

        return self

    def __eq__(self, other):
        if isinstance(other, self.__class__) and len(self.children) == len(other.children):
            for i in range(len(self.children)):
                if self.children[i] != other.children[i]:
                    return False
            return True
        return False


class NotOperator(Operator):
    def calculate_value(self):
        self.value = not self.children[0].calculate_value()
        return self.value

    def get_truth_table_header(self, depth):
        return center(get_operator_symbol(self), 2, depth) + self.children[0].get_truth_table_header(depth + 1)

    def get_truth_table_entry(self, depth):
        return center(self.value, 2, depth) + self.children[0].get_truth_table_entry(depth + 1)

    def not_operator_simplify(self):
        super().not_operator_simplify()

        # Doppelnegation
        if isinstance(self.children[0], NotOperator):
            return self.children[0].children[0].not_operator_simplify()

        # deMorgan
        elif isinstance(self.children[0], AndOperator):
            return OrOperator(list(map(NotOperator, self.children[0].children))).not_operator_simplify()
        elif isinstance(self.children[0], OrOperator):
            return AndOperator(list(map(NotOperator, self.children[0].children))).not_operator_simplify()

        # Negation
        elif self.children[0] == TRUE:
            return FALSE
        elif self.children[0] == FALSE:
            return TRUE

        return self

    def to_nand(self):
        super().to_nand()

        return NandOperator(self.children[0], self.children[0])

    def __str__(self):
        return self.unary_traverse(operators["not"])

    def __eq__(self, other):
        if isinstance(other, NotOperator):
            return self.children == other.children
        return False

    def __hash__(self):
        return hash("not " + self.children[0].name)

    def __gt__(self, other):
        return self.children[0].name > (other.name if isinstance(other, Variable) else other.children[0].name)


class AndOperator(AndOrOperator):
    def calculate_value(self):
        self.value = all([c.calculate_value() for c in self.children])
        return self.value

    def to_nand(self):
        super().to_nand()

        if len(self.children) > 2:
            return OrOperator(
                NandOperator(
                    NandOperator(self.children[0], self.children[1]),
                    NandOperator(self.children[0], self.children[1])
                ),
                *self.children[2:]).to_nand()
        else:
            return NandOperator(
                NandOperator(self.children[0], self.children[1]),
                NandOperator(self.children[0], self.children[1])
            )

    def __str__(self):
        return self.multiple_traverse(operators["and"])


class OrOperator(AndOrOperator):
    def calculate_value(self):
        self.value = any([c.calculate_value() for c in self.children])
        return self.value

    def to_nand(self):
        super().to_nand()

        if len(self.children) > 2:
            return AndOperator(
                NandOperator(
                    NandOperator(self.children[0], self.children[0]),
                    NandOperator(self.children[1], self.children[1])
                ),
                *self.children[2:]).to_nand()
        else:
            return NandOperator(
                NandOperator(self.children[0], self.children[0]),
                NandOperator(self.children[1], self.children[1])
            )

    def __str__(self):
        return self.multiple_traverse(operators["or"])


class XorOperator(Operator):
    def calculate_value(self):
        a = self.children[0].calculate_value()
        b = self.children[1].calculate_value()
        self.value = (a and not b) or (not a and b)
        return self.value

    def replace_with_and_or(self):
        super().replace_with_and_or()

        return AndOperator([
            OrOperator(self.children),
            OrOperator(list(map(NotOperator, self.children)))
        ]).replace_with_and_or()

    def __str__(self):
        return self.multiple_traverse(operators["xor"])


class ImplicationOperator(Operator):
    def calculate_value(self):
        a = self.children[0].calculate_value()
        b = self.children[1].calculate_value()
        self.value = not a or b
        return self.value

    def replace_with_and_or(self):
        super().replace_with_and_or()

        return OrOperator(
            NotOperator(self.children[0]),
            self.children[1]
        ).replace_with_and_or()

    def __str__(self):
        return self.multiple_traverse(operators["implication"])


class BiConditionalOperator(Operator):
    def calculate_value(self):
        a = self.children[0].calculate_value()
        b = self.children[1].calculate_value()
        self.value = (a and b) or (not a and not b)
        return self.value

    def replace_with_and_or(self):
        super().replace_with_and_or()

        return NotOperator(XorOperator(self.children)).replace_with_and_or()

    def __str__(self):
        return self.multiple_traverse(operators["bi-conditional"])


class ITEOperator(Operator):
    def calculate_value(self):
        a = self.children[0].calculate_value()
        b = self.children[1].calculate_value()
        c = self.children[2].calculate_value()
        self.value = (not a or b) and (a or c)
        return self.value

    def get_truth_table_header(self, depth):
        res = center("ITE", 3, depth) + "("
        for child in self.children:
            res += child.get_truth_table_header(depth + 1)
            res += ", "
        res = res[:-2]
        res += ")"
        return res

    def get_truth_table_entry(self, depth):
        res = center(self.value, 3, depth) + "("
        for child in self.children:
            res += child.get_truth_table_entry(depth + 1)
            res += ", "
        res = res[:-2]
        res += ")"
        return res

    def replace_with_and_or(self):
        super().replace_with_and_or()

        return AndOperator(
            ImplicationOperator(self.children[0], self.children[1]),
            ImplicationOperator(NotOperator(self.children[0]), self.children[2])
        ).replace_with_and_or()

    def __str__(self):
        return operators["ite"] + "(" + ", ".join(list(map(str, self.children))) + ")"


class NorOperator(Operator):
    def calculate_value(self):
        self.value = not any([c.calculate_value() for c in self.children])
        return self.value

    def replace_with_and_or(self):
        super().replace_with_and_or()

        return NotOperator(OrOperator(self.children)).replace_with_and_or()

    def __str__(self):
        return self.multiple_traverse(operators["nor"])


class NandOperator(Operator):
    def calculate_value(self):
        self.value = any([not c.calculate_value() for c in self.children])
        return self.value

    def replace_with_and_or(self):
        super().replace_with_and_or()

        return NotOperator(AndOperator(self.children)).replace_with_and_or()

    def __str__(self):
        return self.multiple_traverse(operators["nand"])


operator_classes = {
    operators["not"]: NotOperator,
    operators["and"]: AndOperator,
    operators["or"]: OrOperator,
    operators["xor"]: XorOperator,
    operators["implication"]: ImplicationOperator,
    operators["bi-conditional"]: BiConditionalOperator,
    operators["ite"]: ITEOperator,
    operators["nand"]: NandOperator,
    operators["nor"]: NorOperator,
}
