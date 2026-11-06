class AppError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message
        super().__init__(message)


def account_validation_message(errors, *, password_length=None):
    """Explain account input errors without reflecting passwords or submitted values."""
    messages = []
    for error in errors:
        location = error.get("loc", ())
        field = location[-1] if location else None
        kind, limits = error.get("type"), error.get("ctx", {})
        if field == "email":
            message = "E-mail inválido. Informe um endereço completo, como nome@dominio.com."
        elif field == "password":
            if kind == "missing" or (kind == "string_too_short" and limits.get("min_length") == 1):
                message = "Informe a senha."
            elif kind == "string_too_short":
                received = (
                    f" Foram recebidos {password_length} caracteres."
                    if password_length is not None else ""
                )
                message = f"Senha muito curta.{received} O mínimo é {limits['min_length']} caracteres."
            elif kind == "string_too_long":
                message = f"Senha muito longa. O máximo é {limits['max_length']} caracteres."
            else:
                message = "Informe uma senha válida."
        elif field == "name":
            message = "Informe um nome de 1 a 100 caracteres."
        elif kind == "json_invalid":
            message = "Não foi possível ler os dados de acesso. Envie o formulário novamente."
        else:
            message = "Confira os dados de acesso enviados."
        if message not in messages:
            messages.append(message)
    return " ".join(messages) or "Confira os dados de acesso enviados."
