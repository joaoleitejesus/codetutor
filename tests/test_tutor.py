"""Testes das regras do tutor."""

import unittest

from codetutor.tutor import avaliar_tentativa, corrigir_resposta, validar_formato

MULTIPLA = {"type": "multiple_choice", "correct_option": "b"}
CURTA = {"type": "short_answer", "accepted_answers": ["append", "append()"]}
ACEITA_NONE = {"type": "predict_output", "accepted_answers": ["None"]}
EXERCICIO = {
    "type": "short_answer",
    "accepted_answers": ["append"],
    "hints": ["dica um", "dica dois"],
    "explanation": "explicação",
}


class TestCorrigirResposta(unittest.TestCase):
    def test_multipla_certa(self):
        self.assertTrue(corrigir_resposta(MULTIPLA, "b"))

    def test_multipla_errada(self):
        self.assertFalse(corrigir_resposta(MULTIPLA, "a"))

    def test_texto_ignora_maiusculas_e_espacos(self):
        self.assertTrue(corrigir_resposta(CURTA, "  APPEND  "))

    def test_texto_aceita_variacao(self):
        self.assertTrue(corrigir_resposta(CURTA, "append()"))

    def test_texto_errado(self):
        self.assertFalse(corrigir_resposta(CURTA, "add"))

    def test_resposta_vazia_nao_acerta(self):
        self.assertFalse(corrigir_resposta(CURTA, ""))

    def test_none_nao_acerta_mesmo_se_none_for_resposta_aceita(self):
        self.assertFalse(corrigir_resposta(ACEITA_NONE, None))
        self.assertTrue(corrigir_resposta(ACEITA_NONE, "None"))


class TestValidarFormato(unittest.TestCase):
    def test_multipla_sem_escolha(self):
        self.assertEqual(
            validar_formato(MULTIPLA, None),
            "Escolha uma alternativa antes de responder.",
        )

    def test_multipla_com_escolha(self):
        self.assertIsNone(validar_formato(MULTIPLA, "a"))

    def test_texto_vazio(self):
        self.assertIsNotNone(validar_formato(CURTA, ""))

    def test_texto_so_com_espacos(self):
        self.assertIsNotNone(validar_formato(CURTA, "    "))

    def test_texto_none(self):
        self.assertIsNotNone(validar_formato(CURTA, None))

    def test_texto_com_100_caracteres_e_valido(self):
        self.assertIsNone(validar_formato(CURTA, "a" * 100))

    def test_texto_com_101_caracteres_e_invalido(self):
        self.assertIsNotNone(validar_formato(CURTA, "a" * 101))

    def test_texto_normal(self):
        self.assertIsNone(validar_formato(CURTA, "append"))


class TestAvaliarTentativa(unittest.TestCase):
    def test_primeiro_erro_libera_dica_1(self):
        resultado = avaliar_tentativa(EXERCICIO, "errada", 1)
        self.assertFalse(resultado["correta"])
        self.assertEqual(resultado["dica"], "dica um")
        self.assertIsNone(resultado["explicacao"])
        self.assertFalse(resultado["finalizado"])

    def test_segundo_erro_libera_dica_2(self):
        resultado = avaliar_tentativa(EXERCICIO, "errada", 2)
        self.assertEqual(resultado["dica"], "dica dois")
        self.assertFalse(resultado["finalizado"])

    def test_terceiro_erro_finaliza_com_explicacao(self):
        resultado = avaliar_tentativa(EXERCICIO, "errada", 3)
        self.assertFalse(resultado["correta"])
        self.assertIsNone(resultado["dica"])
        self.assertEqual(resultado["explicacao"], "explicação")
        self.assertTrue(resultado["finalizado"])

    def test_acerto_na_primeira_finaliza(self):
        resultado = avaliar_tentativa(EXERCICIO, "append", 1)
        self.assertTrue(resultado["correta"])
        self.assertIsNone(resultado["dica"])
        self.assertEqual(resultado["explicacao"], "explicação")
        self.assertTrue(resultado["finalizado"])

    def test_acerto_na_segunda_finaliza_sem_dica(self):
        resultado = avaliar_tentativa(EXERCICIO, "append", 2)
        self.assertTrue(resultado["correta"])
        self.assertIsNone(resultado["dica"])
        self.assertTrue(resultado["finalizado"])

    def test_tentativas_zero_levanta_erro(self):
        with self.assertRaises(ValueError):
            avaliar_tentativa(EXERCICIO, "errada", 0)

    def test_tentativas_negativas_levantam_erro(self):
        with self.assertRaises(ValueError):
            avaliar_tentativa(EXERCICIO, "errada", -1)


if __name__ == "__main__":
    unittest.main()
