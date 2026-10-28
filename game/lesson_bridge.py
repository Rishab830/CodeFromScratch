"""Browser transport and a deliberately small Python lesson API."""
import ast
import json
import math
import sys
import types

EDIT_START = "# EDIT START\n"
EDIT_END = "# EDIT END"
MAX_SOURCE = 2000
ALLOWED_ACTIONS = {"jump", "move_left", "move_right", "stop"}


def compile_solution(body):
    if not isinstance(body, str) or len(body) > MAX_SOURCE:
        raise ValueError("Keep your solution under 2,000 characters.")
    source = "def on_blue(player):\n" + body
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError(f"Python syntax error on editable line {max(1, (error.lineno or 2) - 1)}: {error.msg}") from error
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("Keep your code inside on_blue(player).")
    allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Expr,
               ast.Call, ast.Attribute, ast.Name, ast.Load, ast.Pass,
               ast.If, ast.Constant, ast.UnaryOp, ast.Not, ast.BoolOp, ast.And, ast.Or)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError("This lesson uses player actions. Try player.move_left(), player.jump(), or player.stop(). Loops and imports are not needed.")
        if isinstance(node, ast.Call):
            target = node.func
            if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                    and target.value.id == "player" and target.attr in ALLOWED_ACTIONS
                    and not node.args and not node.keywords):
                raise ValueError("Call a player action with no arguments: jump(), move_left(), move_right(), or stop().")
        if isinstance(node, ast.Attribute):
            if not (isinstance(node.value, ast.Name) and node.value.id == "player"
                    and node.attr in ALLOWED_ACTIONS | {"grounded"}):
                raise ValueError("Use only the player actions shown in the reference.")
        if isinstance(node, ast.Name) and node.id != "player":
            raise ValueError("Use player to control the girl.")
    namespace = {"__builtins__": {}}
    exec(compile(tree, "<your-solution>", "exec"), namespace)
    return namespace["on_blue"]


def compile_girl(source, spawn_x, floor):
    """Compile the editable class without exposing the protected game world."""
    if not isinstance(source, str) or len(source) > 8000:
        raise ValueError("Keep your class under 8,000 characters.")
    filename = "<your-Girl-class>"
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError(f"Python syntax error on editable line {error.lineno}: {error.msg}") from error
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.ClassDef) or tree.body[0].name != "Girl":
        raise ValueError("Keep one class named Girl in the green section. The rest of the game is locked.")
    definition = tree.body[0]
    if definition.bases or definition.keywords or definition.decorator_list:
        raise ValueError("Define Girl directly, without inheritance or decorators.")
    allowed = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.arguments, ast.arg,
               ast.Assign, ast.AugAssign, ast.Expr, ast.If, ast.IfExp, ast.Return,
               ast.Pass, ast.Tuple, ast.Load, ast.Store, ast.Call, ast.keyword,
               ast.Attribute, ast.Name, ast.Constant, ast.BinOp, ast.UnaryOp,
               ast.BoolOp, ast.Compare, ast.Add, ast.Sub, ast.Mult, ast.Div,
               ast.FloorDiv, ast.Mod, ast.UAdd, ast.USub, ast.Not, ast.And,
               ast.Or, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
    safe_calls = {"float": float, "int": int, "bool": bool, "abs": abs,
                  "min": min, "max": max, "round": round}
    tuple_assignments = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple):
            tuple_assignments.update((id(node.targets[0]), id(node.value)))
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError("Use class methods, assignments, conditions, and arithmetic. Imports and loops are not needed here.")
        if isinstance(node, ast.Tuple) and id(node) not in tuple_assignments:
            raise ValueError("Use numeric player attributes instead of collections.")
        if isinstance(node, ast.FunctionDef):
            if node.decorator_list or node.args.vararg or node.args.kwarg or (node.name.startswith("__") and node.name != "__init__"):
                raise ValueError("Use ordinary player methods without decorators or special methods other than __init__.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("Use player state inside Girl; runtime internals are not available.")
        if isinstance(node, ast.Attribute) and (not isinstance(node.value, ast.Name) or node.value.id != "self" or node.attr.startswith("__")):
            raise ValueError("Access player attributes through self.")
        if isinstance(node, ast.Call):
            if not ((isinstance(node.func, ast.Name) and node.func.id in safe_calls) or
                    (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "self")):
                raise ValueError("Call your own self methods or basic numeric functions.")
        if isinstance(node, ast.Constant) and (type(node.value) not in (int, float, bool, type(None)) or (type(node.value) in (int, float) and (not math.isfinite(node.value) or abs(node.value) > 10000))):
            raise ValueError("Use finite numeric values and booleans for player state.")
    namespace = {"__builtins__": {"__build_class__": __build_class__, **safe_calls},
                 "__name__": "student_level", "SPAWN_X": spawn_x, "FLOOR": floor}
    exec(compile(tree, filename, "exec"), namespace)
    girl = namespace["Girl"]
    context = {"active": False, "remaining": 0}

    def bounded(method):
        def call(*args, **kwargs):
            if context["active"]:
                return method(*args, **kwargs)
            context.update(active=True, remaining=2000)
            previous_trace = sys.gettrace()

            def trace(frame, event, argument):
                if frame.f_code.co_filename == filename and event in ("call", "line"):
                    context["remaining"] -= 1
                    if context["remaining"] <= 0:
                        raise ValueError("That method did not finish. Check for repeated method calls.")
                return trace

            sys.settrace(trace)
            try:
                return method(*args, **kwargs)
            finally:
                sys.settrace(previous_trace)
                context["active"] = False
        return call

    for name, method in list(vars(girl).items()):
        if isinstance(method, types.FunctionType):
            setattr(girl, name, bounded(method))
    required_methods = ("jump", "move_left", "move_right", "stop")
    if not all(callable(getattr(girl, name, None)) for name in required_methods):
        raise ValueError("Girl needs jump(), move_left(), move_right(), and stop() methods.")
    player = girl()
    for name in ("x", "y", "vx", "vy"):
        value = getattr(player, name, None)
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1000000:
            raise ValueError("Girl needs finite numeric x, y, vx, and vy attributes.")
    if type(getattr(player, "grounded", None)) is not bool:
        raise ValueError("Girl needs a grounded attribute set to True or False.")
    if not all(callable(getattr(player, name, None)) for name in required_methods):
        raise ValueError("Keep the player action methods callable.")
    return girl


def browser():
    if sys.platform == "emscripten":
        import platform
        return platform.window
    return None


def compile_puzzle(body, name, arguments):
    """Compile a small puzzle function; bound loops before they reach the game."""
    if not isinstance(body, str) or len(body) > 8000:
        raise ValueError("Keep your solution under 8,000 characters.")
    filename = "<your-puzzle>"
    try:
        tree = ast.parse(f"def {name}({arguments}):\n" + body)
    except SyntaxError as error:
        raise ValueError(f"Python syntax error on editable line {max(1, (error.lineno or 2) - 1)}: {error.msg}") from error
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("Keep the solution inside the green function body.")
    allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Return,
               ast.Assign, ast.AugAssign, ast.Name, ast.Load, ast.Store, ast.Constant,
               ast.List, ast.Tuple, ast.Dict, ast.Subscript, ast.Expr, ast.Call,
               ast.Attribute, ast.If, ast.IfExp, ast.For, ast.While, ast.Break,
               ast.Continue, ast.Pass, ast.Compare, ast.Eq, ast.NotEq, ast.Lt,
               ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.BoolOp, ast.And,
               ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.UAdd, ast.BinOp,
               ast.Add, ast.Sub, ast.Mod)
    nodes = list(ast.walk(tree))
    if len(nodes) > 600:
        raise ValueError("Keep this puzzle solution small.")
    for node in nodes:
        if not isinstance(node, allowed) or (isinstance(node, ast.FunctionDef) and node is not tree.body[0]):
            raise ValueError("Use values, sequences, conditions, and small loops. Imports and extra functions are not needed.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("Runtime internals are not part of the puzzle.")
        if isinstance(node, ast.Constant) and not (type(node.value) in (bool, type(None)) or
                (type(node.value) in (int, float) and math.isfinite(node.value) and abs(node.value) <= 1000) or
                (isinstance(node.value, str) and len(node.value) <= 64)):
            raise ValueError("Use small numbers and short strings.")
        if isinstance(node, (ast.List, ast.Tuple)) and len(node.elts) > 64:
            raise ValueError("Use at most 64 steps.")
        if isinstance(node, ast.Attribute) and not (isinstance(node.value, ast.Name) and node.attr == "append"):
            raise ValueError("Use local lists and append() for your sequence.")
        if isinstance(node, ast.Call):
            if node.keywords or not ((isinstance(node.func, ast.Name) and node.func.id in {"range", "len", "min", "max", "abs", "int", "bool"}) or
                    (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.attr == "append" and len(node.args) == 1)):
                raise ValueError("Use range(), len(), simple numeric functions, or list.append().")

    def small_range(*args):
        result = range(*args)
        if len(result) > 64:
            raise ValueError("Keep loops to 64 steps or fewer.")
        return result

    namespace = {"__builtins__": {"range": small_range, "len": len, "min": min,
                                  "max": max, "abs": abs, "int": int, "bool": bool}}
    exec(compile(tree, filename, "exec"), namespace)

    def run(*args):
        remaining = 2000
        previous = sys.gettrace()

        def trace(frame, event, argument):
            nonlocal remaining
            if frame.f_code.co_filename == filename and event in ("line", "call"):
                remaining -= 1
                if remaining <= 0:
                    raise ValueError("That loop did not finish. Check its stopping condition.")
            return trace

        sys.settrace(trace)
        try:
            return namespace[name](*args)
        finally:
            sys.settrace(previous)
    return run


def read_input():
    window = browser()
    return str(window.lessonReadInput()) if window is not None else ""


def emit(kind, **data):
    window = browser()
    if window is not None:
        window.lessonEvent(json.dumps({"type": kind, **data}))


def ready():
    emit("ready")


def load_coins(level):
    window = browser()
    if window is not None:
        try:
            saved = json.loads(window.lessonReadCoins(level))
            if isinstance(saved, list):
                return [name for name in saved if isinstance(name, str)]
        except Exception:
            pass
    return []


def save_coins(level, collected):
    window = browser()
    if window is not None:
        window.lessonSaveCoins(level, json.dumps(sorted(collected)))


def poll():
    window = browser()
    if window is not None:
        raw = window.lessonTakeCommand()
        if raw:
            return json.loads(raw)
    return None
