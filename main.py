from app.agent.local_llm import LocalLLM


def main() -> None:
    llm = LocalLLM()

    response = llm.generate(
        "Ответь кратко на русском: что такое локальный AI-агент?"
    )

    print(response)


if __name__ == "__main__":
    main()