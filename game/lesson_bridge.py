"""Browser transport and a deliberately small Python lesson API."""
import ast
import json
import math
import sys

EDIT_START = "    # EDIT START\n"
EDIT_END = "    # EDIT END"
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


def compile_settings(body):
    if not isinstance(body, str) or len(body) > MAX_SOURCE:
        raise ValueError("Keep your code under 2,000 characters.")
    try:
        tree = ast.parse("def configure():\n" + body)
    except SyntaxError as error:
        raise ValueError(f"Python syntax error on editable line {max(1, (error.lineno or 2) - 1)}: {error.msg}") from error
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("Keep your code inside the green section.")
    statements = tree.body[0].body
    if len(statements) != 1 or not isinstance(statements[0], ast.Return):
        raise ValueError("Keep a single return statement with a number.")
    try:
        value = ast.literal_eval(statements[0].value)
    except (ValueError, TypeError):
        raise ValueError("Return a number; the rest of this level’s code is locked.") from None
    if type(value) not in (int, float) or not math.isfinite(value) or not -400 <= value <= -40:
        raise ValueError("Use a finite negative number between -400 and -40.")
    namespace = {"__builtins__": {}}
    exec(compile(tree, "<your-code>", "exec"), namespace)
    return namespace["configure"]


def browser():
    if sys.platform == "emscripten":
        import platform
        return platform.window
    return None


def emit(kind, **data):
    window = browser()
    if window is not None:
        window.lessonEvent(json.dumps({"type": kind, **data}))


def ready():
    emit("ready")


def poll():
    window = browser()
    if window is not None:
        raw = window.lessonTakeCommand()
        if raw:
            return json.loads(raw)
    return None
