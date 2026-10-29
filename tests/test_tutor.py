import unittest

from codetutor.tutor import corrigir_resposta, avaliar_tentativa


class TestTutor(unittest.TestCase):
    def setUp(self):
        self.exercicio = {
            "type": "short_answer",
            "accepted_answers": ["Python"],
            "hints": ["Dica 1", "Dica 2"],
            "explanation": "Explicação",
        }

    def test_corrige_resposta_textual(self):
        self.assertTrue(corrigir_resposta(self.exercicio, "  PYTHON "))
        self.assertFalse(corrigir_resposta(self.exercicio, "Java"))

    def test_libera_dicas_progressivamente(self):
        primeira = avaliar_tentativa(self.exercicio, "Java", 1)
        segunda = avaliar_tentativa(self.exercicio, "Java", 2)

        self.assertEqual(primeira["dica"], "Dica 1")
        self.assertEqual(segunda["dica"], "Dica 2")
        self.assertFalse(primeira["finalizado"])

    def test_encerra_na_terceira_tentativa(self):
        resultado = avaliar_tentativa(self.exercicio, "Java", 3)

        self.assertTrue(resultado["finalizado"])
        self.assertEqual(resultado["explicacao"], "Explicação")

    def test_encerra_quando_acerta(self):
        resultado = avaliar_tentativa(self.exercicio, "Python", 1)

        self.assertTrue(resultado["correta"])
        self.assertTrue(resultado["finalizado"])
        self.assertEqual(resultado["explicacao"], "Explicação")


if __name__ == "__main__":
    unittest.main()