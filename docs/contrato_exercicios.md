# Contrato dos exercícios do CodeTutor

Este arquivo é a regra oficial para escrever exercícios. Quem confere se a regra foi seguida é o código (`codetutor/exercicios.py`), então um exercício fora do padrão é recusado com uma mensagem dizendo o que está errado.

## Onde ficam os arquivos

- Pasta `data/exercicios/`, um arquivo por assunto: `variaveis.json`, `condicionais.json`, `repeticao.json`, `listas.json`, `dicionarios.json`, `arquivos.json`.
- O nome do arquivo (sem `.json`) precisa ser igual ao `topic` de todos os exercícios dentro dele.
- Cada arquivo é uma **lista** `[ ... ]` com um objeto `{ ... }` por exercício, separados por vírgula.
- Salvar em UTF-8 (o padrão do VS Code).

## Campos

| Campo | Obrigatório em | Regra |
|---|---|---|
| `id` | todos | Texto único em todo o projeto. Padrão: sigla do assunto, hífen e número com 3 dígitos (`VAR-001`, `COND-002`, `LOOP-003`, `LIST-004`, `DICT-005`, `FILE-006`). |
| `topic` | todos | Um de: `variaveis`, `condicionais`, `repeticao`, `listas`, `dicionarios`, `arquivos`. |
| `level` | todos | Número **inteiro** 1, 2 ou 3, sem aspas. 1 = reconhecer, 2 = aplicar, 3 = combinar conceitos. |
| `type` | todos | Um de: `multiple_choice`, `predict_output`, `fill_blank`, `short_answer`. |
| `statement` | todos | O enunciado, em texto. Diga sempre o formato da resposta ("responda só com o número"). |
| `code` | `predict_output` e `fill_blank`; opcional nos outros | **Lista de textos, um por linha de código.** Não use `\n`. |
| `options` | só `multiple_choice` | De 2 a 5 alternativas, cada uma `{"id": "a", "text": "..."}`. |
| `correct_option` | só `multiple_choice` | O `id` da alternativa certa. |
| `accepted_answers` | os outros 3 tipos | Lista com pelo menos 1 resposta aceita. |
| `hints` | todos | Lista com **exatamente 2** dicas, da mais leve para a mais direta. |
| `explanation` | todos | Por que a resposta está certa. Aparece depois da terceira tentativa errada ou do acerto. |

Campos que não se aplicam ao tipo **não devem aparecer** (por exemplo, `options` em `short_answer`). Não existe `difficulty`, `correct_answer` nem lista vazia de enfeite.

## Regras por tipo

- **multiple_choice:** não usa `accepted_answers`. Use `correct_option`.
- **predict_output:** a saída esperada tem **uma linha só**. Se o programa imprime várias linhas, mude o exercício para perguntar só uma delas (por exemplo, "o que aparece na última linha?").
- **fill_blank:** o `code` tem **exatamente uma** lacuna, escrita `___` (três underlines). A resposta é o que vai no lugar dela.
- **short_answer:** a resposta é uma palavra ou expressão curta. Coloque em `accepted_answers` as variações que você acha que alguém pode digitar.

## Como o sistema compara respostas de texto

O sistema tira espaços do começo e do fim, ignora maiúsculas e minúsculas e compara com cada item de `accepted_answers`. Ele não entende sentido: `"três"` não é igual a `"3"`. Se duas formas são certas, liste as duas.

## Exemplo completo (fill_blank)

```json
[
  {
    "id": "LOOP-001",
    "topic": "repeticao",
    "level": 1,
    "type": "fill_blank",
    "statement": "Complete a lacuna para exibir os números de 0 a 2. Responda só com o que vai no lugar de ___.",
    "code": [
      "for i in range(___):",
      "    print(i)"
    ],
    "accepted_answers": ["3"],
    "hints": [
      "O limite final do range não é incluído na contagem.",
      "Para gerar 0, 1 e 2, o limite final precisa ser o número seguinte ao 2."
    ],
    "explanation": "range(3) gera 0, 1 e 2, porque o limite superior (3) não entra na contagem."
  }
]
```

Veja os outros três tipos nos arquivos de `data/exercicios/`.

## Erros comuns de JSON

- Vírgula sobrando depois do último item de uma lista ou objeto.
- Falta de vírgula entre dois exercícios ou dois campos.
- Aspas simples no lugar de aspas duplas nas chaves e nos textos do JSON (dentro do texto, o código Python pode usar aspas simples sem problema).
- Aspas duplas **dentro** de um texto sem barra antes (`\"`). Prefira aspas simples no código Python dos exercícios.
- `"level": "1"` com aspas. Precisa ser `1`.

## Como conferir antes de enviar

No Git Bash, dentro da pasta do projeto, com o ambiente virtual ativo:

```
python -m unittest
```

Se aparecer `OK`, o seu arquivo está dentro do contrato. Se aparecer `FAIL` ou `ERROR`, leia a mensagem: ela diz o arquivo, o `id` do exercício e o que está errado.
