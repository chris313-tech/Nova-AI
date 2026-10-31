import json
import os


class NovaMemory:

    def __init__(self):
        self.memory_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "memory.json"
        )

        os.makedirs(
            os.path.dirname(self.memory_file),
            exist_ok=True
        )

        self.memory = self.load_memory()

    def load_memory(self):

        if not os.path.exists(self.memory_file):
            return {}

        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return {}

    def save_memory(self):

        with open(
            self.memory_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.memory,
                file,
                indent=4
            )

    def remember(self, key, value):

        self.memory[key] = value
        self.save_memory()

        return f"I'll remember that, Chris."

    def recall(self, key):

        return self.memory.get(key)

    def forget(self, key):

        if key in self.memory:

            del self.memory[key]
            self.save_memory()

            return f"I've forgotten that, Chris."

        return f"I don't have anything stored about that, Chris."

    def get_all_memory(self):

        return self.memory