"""Testes do histórico (usam um banco temporário, nunca o real)."""

import csv
import io
import tempfile
import unittest
from pathlib import Path

from codetutor.historico import exportar_csv, listar_historico, registrar_tentativa

EXERCICIO = {"id": "VAR-001", "topic": "variaveis", "level": 1}
ERRO = {"correta": False, "finalizado": False}
ACERTO = {"correta": True, "finalizado": True}


class TestHistorico(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        # a subpasta não existe: o código deve criá-la
        self.banco = Path(self.pasta.name) / "dados" / "teste.db"

    def test_banco_novo_comeca_vazio(self):
        self.assertEqual(listar_historico(self.banco), [])

    def test_registra_e_lista_na_ordem(self):
        registrar_tentativa(self.banco, "p01", EXERCICIO, 1, ERRO)
        registrar_tentativa(self.banco, "p01", EXERCICIO, 2, ACERTO)
        historico = listar_historico(self.banco)
        self.assertEqual([h["tentativa"] for h in historico], [1, 2])
        self.assertEqual(historico[0]["correta"], 0)
        self.assertEqual(historico[1]["correta"], 1)
        self.assertEqual(historico[1]["finalizado"], 1)
        self.assertEqual(historico[0]["assunto"], "variaveis")
        self.assertEqual(historico[0]["nivel"], 1)

    def test_filtra_por_participante(self):
        registrar_tentativa(self.banco, "p01", EXERCICIO, 1, ACERTO)
        registrar_tentativa(self.banco, "p02", EXERCICIO, 1, ERRO)
        self.assertEqual(len(listar_historico(self.banco, "p02")), 1)
        self.assertEqual(len(listar_historico(self.banco)), 2)

    def test_dados_ficam_guardados_entre_conexoes(self):
        registrar_tentativa(self.banco, "p01", EXERCICIO, 1, ACERTO)
        # nova chamada abre uma conexão nova: o dado precisa ter sido gravado
        self.assertEqual(len(listar_historico(self.banco)), 1)

    def test_aspas_e_texto_estranho_nao_quebram(self):
        registrar_tentativa(self.banco, "x'); DROP TABLE tentativas;--", EXERCICIO, 1, ERRO)
        self.assertEqual(len(listar_historico(self.banco)), 1)

    def test_exportar_csv_tem_cabecalho_e_linhas(self):
        registrar_tentativa(self.banco, "p01", EXERCICIO, 1, ACERTO)
        linhas = list(csv.DictReader(io.StringIO(exportar_csv(self.banco))))
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["participante"], "p01")
        self.assertEqual(linhas[0]["exercicio_id"], "VAR-001")


if __name__ == "__main__":
    unittest.main()
