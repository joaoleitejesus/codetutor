"""Histórico na nuvem (Supabase), usando só a biblioteca padrão do Python.

Por que existe: no Streamlit Cloud o arquivo SQLite é apagado quando o app dorme,
reinicia ou é atualizado. O Supabase guarda os dados fora do app.

Todas as funções recebem a url e a chave. Em caso de falha de rede, devolvem
False ou None em vez de derrubar o app: o histórico local continua funcionando.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

TABELA = "tentativas"
TEMPO_LIMITE = 8  # segundos
TAMANHO_PAGINA = 1000  # o Supabase devolve no máximo 1000 linhas por pedido


def _cabecalhos(chave, extra=None):
    cabecalhos = {
        "apikey": chave,
        "Authorization": f"Bearer {chave}",
        "Content-Type": "application/json",
    }
    cabecalhos.update(extra or {})
    return cabecalhos


def _endereco(url, parametros=None):
    base = url.rstrip("/") + "/rest/v1/" + TABELA
    if parametros:
        base += "?" + urllib.parse.urlencode(parametros)
    return base


def enviar_tentativa(url, chave, registro):
    """Grava uma tentativa na nuvem. Devolve True se deu certo."""
    pedido = urllib.request.Request(
        _endereco(url),
        data=json.dumps(registro).encode("utf-8"),
        headers=_cabecalhos(chave, {"Prefer": "return=minimal"}),
        method="POST",
    )
    try:
        with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE) as resposta:
            return 200 <= resposta.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def listar_tentativas(url, chave, participante=None):
    """Lê as tentativas da nuvem (da mais antiga à mais nova).

    Devolve None se não conseguiu ler (para o app saber que deve usar o histórico local).
    """
    linhas = []
    inicio = 0
    while True:
        parametros = {"select": "*", "order": "id.asc"}
        if participante is not None:
            parametros["participante"] = "eq." + participante
        pedido = urllib.request.Request(
            _endereco(url, parametros),
            headers=_cabecalhos(
                chave, {"Range-Unit": "items", "Range": f"{inicio}-{inicio + TAMANHO_PAGINA - 1}"}
            ),
            method="GET",
        )
        try:
            with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE) as resposta:
                pagina = json.loads(resposta.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            return None

        linhas.extend(pagina)
        if len(pagina) < TAMANHO_PAGINA:
            return linhas
        inicio += TAMANHO_PAGINA
