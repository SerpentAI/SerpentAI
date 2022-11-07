import ast
import inspect


class Pluggable:

    def __init__(self, **kwargs):
        pass

    @staticmethod
    def allowed_decorators():
        return ["accepted", "expected", "forbidden"]

    @classmethod
    def method_directives(cls):
        directives = {
            "accepted": cls.methods_with_decorator("accepted"),
            "expected": cls.methods_with_decorator("expected"),
            "forbidden": cls.methods_with_decorator("forbidden")
        }

        methods = cls._find_decorators()

        for name, decorators in methods.items():
            if name == "__init__":
                continue

            if not len(decorators):
                directives["forbidden"].append(name)

        return directives

    @classmethod
    def methods_with_decorator(cls, decorator):
        methods = list()

        if decorator not in cls.allowed_decorators():
            return methods

        decorated_methods = cls._find_decorators()

        for method, decorator_structure in decorated_methods.items():
            decorator_structure_string = " ".join(decorator_structure) or ""

            if "attr='%s'" % decorator in decorator_structure_string:
                methods.append(method)

        return methods

    @classmethod
    def _find_decorators(cls):
        result = dict()

        def visit_FunctionDef(node):
            result[node.name] = [ast.dump(e) for e in node.decorator_list]

        v = ast.NodeVisitor()

        v.visit_FunctionDef = visit_FunctionDef
        v.visit(compile(inspect.getsource(cls), '?', 'exec', ast.PyCF_ONLY_AST))

        return result

    @classmethod
    def on_file_install(cls, **kwargs):
        print("CALLBACK: on_file_install", kwargs)

    @classmethod
    def on_file_uninstall(cls, **kwargs):
        print("CALLBACK: on_file_uninstall", kwargs)

