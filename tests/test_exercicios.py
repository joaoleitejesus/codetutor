"""Testes do validador e do carregador de exercícios."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from codetutor.exercicios import carregar_exercicios, validar_exercicio

PASTA_EXERCICIOS = Path(__file__).resolve().parent.parent / "data" / "exercicios"

# Um exemplo válido de cada tipo. Os testes copiam e estragam um campo por vez.
MULTIPLA = {
    "id": "T-001",
    "topic": "variaveis",
    "level": 1,
    "type": "multiple_choice",
    "statement": "Quanto vale x?",
    "code": ["x = 1"],
    "options": [{"id": "a", "text": "1"}, {"id": "b", "text": "2"}],
    "correct_option": "a",
    "hints": ["dica um", "dica dois"],
    "explanation": "x recebe 1.",
}
SAIDA = {
    "id": "T-002",
    "topic": "condicionais",
    "level": 2,
    "type": "predict_output",
    "statement": "O que aparece?",
    "code": ["print('oi')"],
    "accepted_answers": ["oi"],
    "hints": ["dica um", "dica dois"],
    "explanation": "print mostra oi.",
}
LACUNA = {
    "id": "T-003",
    "topic": "repeticao",
    "level": 3,
    "type": "fill_blank",
    "statement": "Complete.",
    "code": ["for i in range(___):", "    print(i)"],
    "accepted_answers": ["3"],
    "hints": ["dica um", "dica dois"],
    "explanation": "range(3).",
}
CURTA = {
    "id": "T-004",
    "topic": "listas",
    "level": 1,
    "type": "short_answer",
    "statement": "Qual método?",
    "accepted_answers": ["append"],
    "hints": ["dica um", "dica dois"],
    "explanation": "append.",
}


def com(exercicio, **mudancas):
    """Devolve uma cópia do exercício com os campos alterados."""
    novo = copy.deepcopy(exercicio)
    novo.update(mudancas)
    return novo


def sem(exercicio, campo):
    """Devolve uma cópia do exercício sem um campo."""
    novo = copy.deepcopy(exercicio)
    del novo[campo]
    return novo


class TestValidarExercicio(unittest.TestCase):
    def test_exemplos_validos_nao_tem_erros(self):
        for exemplo in (MULTIPLA, SAIDA, LACUNA, CURTA):
            with self.subTest(tipo=exemplo["type"]):
                self.assertEqual(validar_exercicio(exemplo), [])

    def test_code_e_opcional_em_multipla_e_resposta_curta(self):
        self.assertEqual(validar_exercicio(sem(MULTIPLA, "code")), [])
        self.assertEqual(validar_exercicio(com(CURTA, code=["x = 1"])), [])

    def test_nao_e_objeto(self):
        self.assertTrue(validar_exercicio("texto"))
        self.assertTrue(validar_exercicio(None))

    def test_tipo_invalido_ou_ausente(self):
        self.assertTrue(validar_exercicio(com(CURTA, type="verdadeiro_falso")))
        self.assertTrue(validar_exercicio(sem(CURTA, "type")))
        self.assertTrue(validar_exercicio(com(CURTA, type=["short_answer"])))

    def test_campo_obrigatorio_ausente(self):
        for campo in ("id", "topic", "level", "statement", "hints", "explanation"):
            with self.subTest(campo=campo):
                erros = validar_exercicio(sem(CURTA, campo))
                self.assertIn(f"campo obrigatório ausente: {campo}", erros)

    def test_campo_nao_permitido(self):
        erros = validar_exercicio(com(CURTA, options=[]))
        self.assertIn("campo não permitido para short_answer: options", erros)
        erros = validar_exercicio(com(MULTIPLA, accepted_answers=["a"]))
        self.assertIn("campo não permitido para multiple_choice: accepted_answers", erros)
        erros = validar_exercicio(com(CURTA, dificuldade="facil"))
        self.assertIn("campo não permitido para short_answer: dificuldade", erros)

    def test_topic_invalido(self):
        self.assertTrue(validar_exercicio(com(CURTA, topic="laços")))

    def test_level_precisa_ser_inteiro_de_1_a_3(self):
        for ruim in (0, 4, "1", 1.0, True, None):
            with self.subTest(level=ruim):
                self.assertTrue(validar_exercicio(com(CURTA, level=ruim)))

    def test_textos_nao_podem_ser_vazios(self):
        for campo in ("id", "statement", "explanation"):
            with self.subTest(campo=campo):
                self.assertTrue(validar_exercicio(com(CURTA, **{campo: "   "})))

    def test_hints_exige_exatamente_duas_dicas(self):
        self.assertTrue(validar_exercicio(com(CURTA, hints=["só uma"])))
        self.assertTrue(validar_exercicio(com(CURTA, hints=["a", "b", "c"])))
        self.assertTrue(validar_exercicio(com(CURTA, hints=["a", ""])))
        self.assertTrue(validar_exercicio(com(CURTA, hints="uma dica")))

    def test_code_precisa_ser_lista_de_textos(self):
        self.assertTrue(validar_exercicio(com(SAIDA, code="print('oi')")))
        self.assertTrue(validar_exercicio(com(SAIDA, code=[])))
        self.assertTrue(validar_exercicio(com(SAIDA, code=["ok", 3])))

    def test_predict_output_e_fill_blank_exigem_code(self):
        self.assertTrue(validar_exercicio(sem(SAIDA, "code")))
        self.assertTrue(validar_exercicio(sem(LACUNA, "code")))

    def test_accepted_answers(self):
        for ruim in ([], [""], "append", [1], None):
            with self.subTest(valor=ruim):
                self.assertTrue(validar_exercicio(com(CURTA, accepted_answers=ruim)))

    def test_lacuna_exige_exatamente_uma(self):
        sem_lacuna = com(LACUNA, code=["for i in range(3):", "    print(i)"])
        duas_lacunas = com(LACUNA, code=["for i in range(___):", "    print(___)"])
        self.assertIn("fill_blank deve ter exatamente uma lacuna ___ em code",
                      validar_exercicio(sem_lacuna))
        self.assertIn("fill_blank deve ter exatamente uma lacuna ___ em code",
                      validar_exercicio(duas_lacunas))

    def test_alternativas(self):
        # correct_option que não existe nas alternativas
        self.assertTrue(validar_exercicio(com(MULTIPLA, correct_option="z")))
        # ids repetidos
        repetidas = [{"id": "a", "text": "1"}, {"id": "a", "text": "2"}]
        self.assertTrue(validar_exercicio(com(MULTIPLA, options=repetidas)))
        # só uma alternativa
        self.assertTrue(validar_exercicio(com(MULTIPLA, options=[{"id": "a", "text": "1"}])))
        # alternativa sem o campo text
        self.assertTrue(validar_exercicio(com(MULTIPLA, options=[{"id": "a"}, {"id": "b"}])))
        # options que não é lista
        self.assertTrue(validar_exercicio(com(MULTIPLA, options="a, b")))


class TestCarregarExercicios(unittest.TestCase):
    def _pasta_com(self, arquivos):
        """Cria uma pasta temporária com os arquivos {nome: conteúdo} e devolve o caminho."""
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        for nome, conteudo in arquivos.items():
            texto = conteudo if isinstance(conteudo, str) else json.dumps(conteudo)
            (Path(pasta.name) / nome).write_text(texto, encoding="utf-8")
        return pasta.name

    def test_banco_real_do_projeto_esta_dentro_do_contrato(self):
        exercicios = carregar_exercicios(PASTA_EXERCICIOS)
        self.assertGreater(len(exercicios), 0)

    def test_carrega_arquivos_validos(self):
        pasta = self._pasta_com({
            "variaveis.json": [MULTIPLA],
            "condicionais.json": [SAIDA],
        })
        self.assertEqual(len(carregar_exercicios(pasta)), 2)

    def test_pasta_vazia_devolve_lista_vazia(self):
        self.assertEqual(carregar_exercicios(self._pasta_com({})), [])

    def test_json_quebrado(self):
        pasta = self._pasta_com({"listas.json": '[{"id": "X",}]'})
        with self.assertRaises(ValueError) as contexto:
            carregar_exercicios(pasta)
        self.assertIn("JSON inválido", str(contexto.exception))

    def test_arquivo_que_nao_e_lista(self):
        pasta = self._pasta_com({"listas.json": CURTA})
        with self.assertRaises(ValueError) as contexto:
            carregar_exercicios(pasta)
        self.assertIn("deve conter uma lista", str(contexto.exception))

    def test_id_repetido_entre_arquivos(self):
        pasta = self._pasta_com({
            "variaveis.json": [com(MULTIPLA, id="DUP-1")],
            "listas.json": [com(CURTA, id="DUP-1")],
        })
        with self.assertRaises(ValueError) as contexto:
            carregar_exercicios(pasta)
        self.assertIn("id repetido", str(contexto.exception))

    def test_topic_diferente_do_nome_do_arquivo(self):
        pasta = self._pasta_com({"variaveis.json": [CURTA]})
        with self.assertRaises(ValueError) as contexto:
            carregar_exercicios(pasta)
        self.assertIn("topic deve ser igual ao nome do arquivo", str(contexto.exception))

    def test_mensagem_aponta_arquivo_e_id(self):
        pasta = self._pasta_com({"listas.json": [com(CURTA, level=9)]})
        with self.assertRaises(ValueError) as contexto:
            carregar_exercicios(pasta)
        self.assertIn("listas.json [T-004]", str(contexto.exception))

    def test_aceita_arquivo_salvo_com_bom(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        caminho = Path(pasta.name) / "listas.json"
        caminho.write_text(json.dumps([CURTA]), encoding="utf-8-sig")
        self.assertEqual(len(carregar_exercicios(pasta.name)), 1)


if __name__ == "__main__":
    unittest.main()
