import ast

def show_style_corrected(code):
    try:
        tree = ast.parse(code)
        clean_code = ast.unparse(tree)

        return {
            "success": True,
            "corrected_code": clean_code
        }

    except SyntaxError as e:
        return {
            "success": False,
            "corrected_code": code
        }