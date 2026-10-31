# =========================================================
# NOVA AI BRAIN
# =========================================================

class NovaBrain:

    def __init__(self):
        self.name = "Nova"
        self.user_name = "Chris"

    def think(self, text):

        text = text.lower().strip()

        # Greetings
        if any(word in text for word in [
            "hello",
            "hi",
            "hey",
            "hey nova",
            "hello nova"
        ]):
            return "Hello Chris. How can I help you?"

        # Nova's name
        if (
            "what is your name" in text
            or "what's your name" in text
            or "can you tell me your name" in text
            or "who are you" in text
            or "what are you called" in text
        ):
            return "My name is Nova."

        # User's name
        if (
            "what is my name" in text
            or "what's my name" in text
            or "do you know my name" in text
            or "who am i" in text
        ):
            return "Your name is Chris."

        # How Nova is doing
        if (
            "how are you" in text
            or "how are you doing" in text
            or "how do you feel" in text
        ):
            return "I'm doing great, Chris. Thanks for asking."

        # Remember something
        if (
            text.startswith("remember that")
            or text.startswith("remember this")
            or text.startswith("remember")
        ):
            return "I can remember that, Chris."

        # Ask Nova to recall something
        if (
            text.startswith("what do you remember")
            or text.startswith("do you remember")
            or text.startswith("what did i tell you")
        ):
            return "I can check my memory, Chris."

        # Forget something
        if (
            text.startswith("forget that")
            or text.startswith("forget this")
            or text.startswith("forget")
        ):
            return "I can forget that, Chris."

        # Thanks
        if any(phrase in text for phrase in [
            "thank you",
            "thanks",
            "thanks nova",
            "thank you nova"
        ]):
            return "You're welcome, Chris. I'm always happy to help."

        # Goodbye
        if any(phrase in text for phrase in [
            "goodbye",
            "bye",
            "see you later",
            "good night"
        ]):
            return "Goodbye, Chris."

        # Unknown
        return "I understand what you said, but I don't know how to respond to that yet."
