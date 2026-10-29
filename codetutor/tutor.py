def corrigir_resposta(exercicio, resposta):
    """Verifica se a resposta do aluno está correta."""

    if exercicio["type"] == "multiple_choice":
        return resposta == exercicio["correct_option"]

    resposta = str(resposta).strip().lower()

    respostas_aceitas = exercicio["accepted_answers"]

    return resposta in [
        aceita.strip().lower()
        for aceita in respostas_aceitas
    ]
def avaliar_tentativa(exercicio, resposta, tentativas):
    """Avalia a resposta e informa o próximo passo do tutor."""

    correta = corrigir_resposta(exercicio, resposta)

    if correta:
        return {
            "correta": True,
            "mensagem": "Resposta correta!",
            "dica": None,
            "explicacao": exercicio["explanation"],
            "finalizado": True,
        }

    if tentativas >= 3:
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