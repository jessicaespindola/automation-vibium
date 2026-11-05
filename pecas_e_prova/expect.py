"""Asserções com mensagem, sem depender de um framework de teste."""


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
