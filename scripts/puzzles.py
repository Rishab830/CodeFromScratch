"""Starting bugs for the five later adventures. Each region is compiled as Python."""
PUZZLES = {
    3: ("confused-traffic-signal", "next_light", "current", '''    transitions = {"red": "yellow", "yellow": "red", "green": "red"}
    return transitions[current]
'''),
    4: ("lost-robot", "robot_program", "", '''    return ["right", "down", "left", "up"]
'''),
    5: ("endless-coin-collector", "should_collect", "count", '''    return count >= 0
'''),
    6: ("wrong-door", "choose_door", "password", '''    if password == "STAR":
        return 0
    return 2
'''),
    7: ("final-escape", "escape_plan", "", '''    steps = []
    for cell in range(2):
        steps.append("power")
    if len(steps) == 3:
        steps.append("open")
        steps.append("unlock")
    return steps
'''),
}
