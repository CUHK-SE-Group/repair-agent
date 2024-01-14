import ast

class RevisedASTNormalizer(ast.NodeTransformer):
    def __init__(self):
        self.variable_counter = 1
        self.variable_map = {}

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) or isinstance(node.ctx, ast.Load):
            if node.id not in self.variable_map:
                self.variable_map[node.id] = f'var{self.variable_counter}'
                self.variable_counter += 1
            node.id = self.variable_map[node.id]
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float, str)):
            node.value = 0  # replace literals with a placeholder
        return node

def get_revised_normalized_ast(code):
    tree = ast.parse(code)
    normalizer = RevisedASTNormalizer()
    normalized_tree = normalizer.visit(tree)
    ast.fix_missing_locations(normalized_tree)
    return ast.dump(normalized_tree)

code1 = """
num1 = 10
num2 = 20
sum = num1 + num2
print(sum)
"""

code2 = """
a = 100
b = 200
result = a + b
print(result)
"""

revised_normalized_ast1 = get_revised_normalized_ast(code1)
revised_normalized_ast2 = get_revised_normalized_ast(code2)

revised_normalized_asts_identical = revised_normalized_ast1 == revised_normalized_ast2

print("The ASTs are identical" if revised_normalized_asts_identical else "The ASTs are different")
print("\nNormalized AST:")
print(revised_normalized_ast1)
