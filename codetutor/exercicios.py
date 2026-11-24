"""Carrega e valida os exercícios do CodeTutor.

O contrato (campos, tipos e regras) está em docs/contrato_exercicios.md.
"""

import json
from pathlib import Path

ASSUNTOS = {"variaveis", "condicionais", "repeticao", "listas", "dicionarios", "arquivos"}
TIPOS = {"multiple_choice", "predict_output", "fill_blank", "short_answer"}
NIVEIS = {1, 2, 3}

# Campos que todo exercício precisa ter, qualquer que seja o tipo.
CAMPOS_COMUNS = {"id", "topic", "level", "type", "statement", "hints", "explanation"}

# Campos extras obrigatórios de cada tipo.
CAMPOS_POR_TIPO = {
    "multiple_choice": {"options", "correct_option"},
    "predict_output": {"accepted_answers"},
    "fill_blank": {"accepted_answers"},
    "short_answer": {"accepted_answers"},
}

# Campo que pode existir ou não, em qualquer tipo.
CAMPOS_OPCIONAIS = {"code"}


def _texto_valido(valor):
    """Devolve True se o valor é um texto que não está vazio."""
    return isinstance(valor, str) and valor.strip() != ""


def _validar_alternativas(opcoes, correta):
    """Confere as alternativas de uma múltipla escolha e devolve a lista de erros."""
    if not isinstance(opcoes, list) or not 2 <= len(opcoes) <= 5:
        return ["options deve ser uma lista de 2 a 5 alternativas"]

    ids = []
    for alternativa in opcoes:
        if not isinstance(alternativa, dict) or set(alternativa) != {"id", "text"}:
            return ["cada alternativa deve ter exatamente os campos id e text"]
        if not (_texto_valido(alternativa["id"]) and _texto_valido(alternativa["text"])):
            return ["id e text de cada alternativa devem ser textos não vazios"]
        ids.append(alternativa["id"])

    erros = []
    if len(set(ids)) != len(ids):
        erros.append("os ids das alternativas devem ser únicos")
    if correta not in ids:
        erros.append("correct_option deve ser o id de uma das alternativas")
    return erros


def validar_exercicio(exercicio):
    """Confere um exercício e devolve a lista de erros (vazia se estiver tudo certo)."""
    if not isinstance(exercicio, dict):
        return ["o exercício deve ser um objeto JSON (entre chaves { })"]

    tipo = exercicio.get("type")
    if not isinstance(tipo, str) or tipo not in TIPOS:
        return [f"type inválido: {tipo!r}"]

    # 1) Quais campos existem? Faltando ou sobrando, já paramos aqui.
    obrigatorios = CAMPOS_COMUNS | CAMPOS_POR_TIPO[tipo]
    permitidos = obrigatorios | CAMPOS_OPCIONAIS
    presentes = set(exercicio)

    erros = []
    for campo in sorted(obrigatorios - presentes):
        erros.append(f"campo obrigatório ausente: {campo}")
    for campo in sorted(presentes - permitidos):
        erros.append(f"campo não permitido para {tipo}: {campo}")
    if erros:
        return erros

    # 2) Os valores de cada campo fazem sentido?
    if not _texto_valido(exercicio["id"]):
        erros.append("id deve ser um texto não vazio")
    if not isinstance(exercicio["topic"], str) or exercicio["topic"] not in ASSUNTOS:
        erros.append(f"topic inválido: {exercicio['topic']!r}")
    if type(exercicio["level"]) is not int or exercicio["level"] not in NIVEIS:
        erros.append("level deve ser o número inteiro 1, 2 ou 3")
    if not _texto_valido(exercicio["statement"]):
        erros.append("statement deve ser um texto não vazio")
    if not _texto_valido(exercicio["explanation"]):
        erros.append("explanation deve ser um texto não vazio")

    dicas = exercicio["hints"]
    if not (isinstance(dicas, list) and len(dicas) == 2 and all(_texto_valido(d) for d in dicas)):
        erros.append("hints deve ser uma lista com exatamente 2 textos não vazios")

    codigo = exercicio.get("code")
    codigo_valido = isinstance(codigo, list) and len(codigo) > 0 and all(isinstance(l, str) for l in codigo)
    if "code" in exercicio and not codigo_valido:
        erros.append("code deve ser uma lista de textos, um por linha de código")

    # 3) Regras específicas de cada tipo.
    if tipo == "multiple_choice":
        erros += _validar_alternativas(exercicio["options"], exercicio["correct_option"])
    else:
        respostas = exercicio["accepted_answers"]
        if not (isinstance(respostas, list) and respostas and all(_texto_valido(r) for r in respostas)):
            erros.append("accepted_answers deve ser uma lista com ao menos 1 texto não vazio")

    if tipo in ("predict_output", "fill_blank") and "code" not in exercicio:
        erros.append(f"{tipo} exige o campo code")
    if tipo == "fill_blank" and codigo_valido:
        if "\n".join(codigo).count("___") != 1:
            erros.append("fill_blank deve ter exatamente uma lacuna ___ em code")

    return erros


def carregar_exercicios(pasta):
    """Lê todos os arquivos .json da pasta e devolve a lista de exercícios.

    Se algo estiver fora do contrato, levanta ValueError com todos os problemas
    de uma vez, dizendo o arquivo e o id de cada exercício.
    """
    exercicios = []
    problemas = []
    ids_vistos = set()

    for arquivo in sorted(Path(pasta).glob("*.json")):
        try:
            # utf-8-sig aceita arquivos salvos com ou sem BOM (comum no Windows).
            with open(arquivo, encoding="utf-8-sig") as f:
                lista = json.load(f)
        except json.JSONDecodeError as erro:
            problemas.append(f"{arquivo.name}: JSON inválido ({erro})")
            continue

        if not isinstance(lista, list):
            problemas.append(f"{arquivo.name}: o arquivo deve conter uma lista [ ]")
            continue

        for posicao, exercicio in enumerate(lista, start=1):
            if isinstance(exercicio, dict):
                nome = exercicio.get("id", f"item {posicao}")
            else:
                nome = f"item {posicao}"
            local = f"{arquivo.name} [{nome}]"

            for erro in validar_exercicio(exercicio):
                problemas.append(f"{local}: {erro}")

            if isinstance(exercicio, dict):
                if exercicio.get("topic") != arquivo.stem:
                    problemas.append(
                        f"{local}: topic deve ser igual ao nome do arquivo ({arquivo.stem})"
                    )
                id_exercicio = exercicio.get("id")
                if isinstance(id_exercicio, str):
                    if id_exercicio in ids_vistos:
                        problemas.append(f"{local}: id repetido")
                    ids_vistos.add(id_exercicio)

            exercicios.append(exercicio)

    if problemas:
        raise ValueError("Exercícios fora do contrato:\n" + "\n".join(problemas))
    return exercicios


ORDEM_ASSUNTOS = ["variaveis", "condicionais", "repeticao", "listas", "dicionarios", "arquivos"]


def ordenar_exercicios(exercicios):
    """Ordena por assunto (ordem didática), depois nível, depois id.

    Assim todo participante vê a mesma sequência, do mais básico ao mais difícil.
    """
    return sorted(
        exercicios,
        key=lambda ex: (ORDEM_ASSUNTOS.index(ex["topic"]), ex["level"], ex["id"]),
    )
