"""Regras do tutor: correção de respostas e decisões de ensino."""

MAX_TENTATIVAS = 3
TAMANHO_MAXIMO_RESPOSTA = 100


def corrigir_resposta(exercicio, resposta):
    """Verifica se a resposta do aluno está correta."""

    if exercicio["type"] == "multiple_choice":
        return resposta == exercicio["correct_option"]

    # Nos outros tipos a resposta é um texto. Qualquer outra coisa (como None) está errada.
    if not isinstance(resposta, str):
        return False

    resposta = resposta.strip().lower()

    return resposta in [
        aceita.strip().lower()
        for aceita in exercicio["accepted_answers"]
    ]


def validar_formato(exercicio, resposta):
    """Confere o formato da resposta antes de corrigir.

    Devolve uma mensagem de erro se o formato é inválido, ou None se está tudo certo.
    Resposta com formato inválido não gasta tentativa.
    """

    if exercicio["type"] == "multiple_choice":
        if resposta is None:
            return "Escolha uma alternativa antes de responder."
        return None

    if not isinstance(resposta, str) or resposta.strip() == "":
        return "Digite uma resposta antes de enviar."

    if len(resposta) > TAMANHO_MAXIMO_RESPOSTA:
        return f"A resposta deve ter no máximo {TAMANHO_MAXIMO_RESPOSTA} caracteres."

    return None


def avaliar_tentativa(exercicio, resposta, tentativas):
    """Avalia a resposta e informa o próximo passo do tutor.

    tentativas é o número da tentativa atual, contando esta (1, 2 ou 3).
    """

    if tentativas < 1:
        raise ValueError("tentativas deve ser 1 ou mais")

    correta = corrigir_resposta(exercicio, resposta)

    if correta:
        return {
            "correta": True,
            "mensagem": "Resposta correta!",
            "dica": None,
            "explicacao": exercicio["explanation"],
            "finalizado": True,
        }

    if tentativas >= MAX_TENTATIVAS:
        return {
            "correta": False,
            "mensagem": "Você atingiu o limite de tentativas.",
            "dica": None,
            "explicacao": exercicio["explanation"],
            "finalizado": True,
        }

    dica = exercicio["hints"][tentativas - 1]

    return {
        "correta": False,
        "mensagem": "Ainda não. Tente novamente!",
        "dica": dica,
        "explicacao": None,
        "finalizado": False,
    }


def proximo_indice(exercicios, historico):
    """Posição do primeiro exercício que o participante ainda não concluiu.

    'historico' é a lista de tentativas dele. Devolve None se concluiu todos.
    """
    concluidos = {linha["exercicio_id"] for linha in historico if linha["finalizado"]}
    for posicao, exercicio in enumerate(exercicios):
        if exercicio["id"] not in concluidos:
            return posicao
    return None
