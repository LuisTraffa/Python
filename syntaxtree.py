from parser import parse

root = parse("ITE(true, B, C)")
operators = {
    "not": "¬",
    "and": "∧",
    "or": "∨",
    "xor": "⊕",
    "implication": "→",
    "bi-conditional": "↔",
    "ite": "ITE"
}
if __name__ == "__main__":
    print(root)
    root = root.simplify()
    print(root)
