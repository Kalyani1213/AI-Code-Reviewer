import ast

class ErrorFinder(ast.NodeVisitor):
    """
    WHAT IT DOES: Walks through code and finds problems
    """
    def __init__(self):
        self.errors = []
        self.defined_vars = set()
        self.used_vars = set()

    def visit_Assign(self, node):
        """When we see: x = 5"""    
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars.add(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        """When we see a variable being used"""
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        self.generic_visit(node)

    def find_unused_variables(self):
        """After visiting, check for unused vars"""
        unused = self.defined_vars - self.used_vars
        for var in unused:
            self.errors.append({
                "type": "UnusedVariable",
                "line": "Unknown",
                "message": f"Variable '{var}' is defined but never used",
                "suggestion": f"Remove '{var} or use it in your code"
            })
        return self.errors

def detect_errors(code_string):
    """Main function you'll call"""
    try:
        tree = ast.parse(code_string)
        finder = ErrorFinder()

        finder.visit(tree)

        errors = finder.find_unused_variables()

        return {
            "success": True,
            "errors": errors,
            "error_count": len(errors)
        }

    except SyntaxError as e:
        return {
            "success": False
        }