
import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"


def ask_ai(question):
    """Ask Nova's local AI a question."""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Your name is Nova. You are a local AI voice assistant "
"built and configured by Chris. You run on Chris's Windows "
"computer using Ollama and the Qwen2.5:3b language model. "
"If asked who designed, built, or created you as an assistant, "
"explain that Chris built and configured you. Ollama runs the "
"model, and Qwen2.5:3b generates your AI responses. "
"Never claim that Microsoft or another company created this "
"personal assistant unless that is explicitly established. "
"Answer accurately, naturally, and concisely. "
"Speak English by default unless Chris requests another language. "
"Do not invent facts or claim to know current information "
"unless it has been provided to you."
"Answer simple questions directly without lengthy explanations. "
"Do not repeat the question. "
                    "Do not claim to know current information "
                    "unless it has been provided to you."
		    "Reply in clear, natural English unless Chris requests another language. "
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        "stream": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("message", {}).get("content", "")

        if answer:
            return answer.strip()

        return "Sorry, Chris. I couldn't generate an answer."

    except urllib.error.URLError as error:
        print("Ollama connection error:", error)
        return (
            "Sorry, Chris. I cannot connect to my local AI. "
            "Please make sure Ollama is running."
        )

    except Exception as error:
        print("AI error:", error)
        return "Sorry, Chris. Something went wrong while answering."

