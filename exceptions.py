"""Кастомные классы обработки ошибок."""


class UndocumentedStatusError(Exception):
    """Недокументированный статус домашней работы."""

    ...


class EmptyStatusError(Exception):
    """Отсутствует статус домашней работы."""

    ...
