"""Histórico de tentativas dos alunos, guardado em SQLite.

Todas as funções recebem o caminho do banco. Se um dia o histórico for para um
banco na nuvem (Postgres), só este arquivo muda: o app continua chamando as
mesmas funções.
"""

import csv
import io
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).parent.parent / "data" / "historico.db"

COLUNAS = [
    "participante",
    "exercicio_id",
    "assunto",
    "nivel",
    "tentativa",
    "correta",
    "finalizado",
    "data_hora",
]


def _conectar(caminho):
    """Abre o banco (criando pasta e tabela se for a primeira vez)."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(caminho)
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS tentativas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participante TEXT NOT NULL,
            exercicio_id TEXT NOT NULL,
            assunto TEXT NOT NULL,
            nivel INTEGER NOT NULL,
            tentativa INTEGER NOT NULL,
            correta INTEGER NOT NULL,
            finalizado INTEGER NOT NULL,
            data_hora TEXT NOT NULL
        )
        """
    )
    return conexao


def registrar_tentativa(caminho, participante, exercicio, tentativa, resultado):
    """Guarda uma tentativa. 'resultado' é o dicionário de avaliar_tentativa."""
    linha = (
        participante,
        exercicio["id"],
        exercicio["topic"],
        exercicio["level"],
        tentativa,
        int(resultado["correta"]),
        int(resultado["finalizado"]),
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )

    with closing(_conectar(caminho)) as conexao:
        with conexao:  # confirma (commit) a gravação
            conexao.execute(
                "INSERT INTO tentativas (participante, exercicio_id, assunto, nivel, "
                "tentativa, correta, finalizado, data_hora) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                linha,
            )


def listar_historico(caminho, participante=None):
    """Devolve as tentativas (da mais antiga à mais nova) como lista de dicionários."""
    consulta = f"SELECT {', '.join(COLUNAS)} FROM tentativas"
    parametros = ()

    if participante is not None:
        consulta += " WHERE participante = ?"
        parametros = (participante,)

    consulta += " ORDER BY id"

    with closing(_conectar(caminho)) as conexao:
        linhas = conexao.execute(consulta, parametros).fetchall()

    return [dict(zip(COLUNAS, linha)) for linha in linhas]


def exportar_csv(caminho):
    """Devolve todo o histórico como texto CSV (para backup e para a análise)."""
    saida = io.StringIO()
    escritor = csv.DictWriter(saida, fieldnames=COLUNAS)
    escritor.writeheader()
    escritor.writerows(listar_historico(caminho))
    return saida.getvalue()
