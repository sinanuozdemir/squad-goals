class Task:
    def __init__(self, name: str, goal: str):
        self.name = name
        self.goal = goal

    def __str__(self) -> str:
        return f"{self.name}: {self.goal}"
