from pathlib import Path

import streamlit as st

from codetutor.exercicios import carregar_exercicios
from codetutor.tutor import MAX_TENTATIVAS, avaliar_tentativa, validar_formato

PASTA_EXERCICIOS = Path(__file__).parent / "data" / "exercicios"


st.set_page_config(
    page_title="CodeTutor",
    page_icon="🐍",
    layout="centered",
)


st.title("CodeTutor")
st.subheader("Aprenda Python na prática")

st.write(
    "Resolva exercícios, receba dicas e entenda seus erros "
    "enquanto aprende a programar."
)

st.divider()

st.header("Área de estudos")

# 1) Carregar o banco de exercícios
try:
    exercicios = carregar_exercicios(PASTA_EXERCICIOS)
except ValueError as erro:
    st.error("O banco de exercícios tem problemas. Avise quem editou os arquivos.")
    st.code(str(erro))
    st.stop()

if not exercicios:
    st.warning("Nenhum exercício encontrado em data/exercicios.")
    st.stop()

# 2) Memória da sessão: sobrevive aos cliques, ao contrário das variáveis comuns
if "indice" not in st.session_state:
    st.session_state.indice = 0
    st.session_state.tentativas = 0
    st.session_state.resultado = None
    st.session_state.dicas = []

posicao = st.session_state.indice % len(exercicios)
exercicio = exercicios[posicao]
resultado = st.session_state.resultado
finalizado = resultado is not None and resultado["finalizado"]

# 3) Mostrar o exercício
st.caption(
    f"Exercício {posicao + 1} de {len(exercicios)} | "
    f"Assunto: {exercicio['topic']} | Nível {exercicio['level']}"
)
st.markdown(exercicio["statement"])

if "code" in exercicio:
    st.code("\n".join(exercicio["code"]), language="python")

# 4) Campo de resposta (a chave inclui o id para cada exercício ter o seu campo)
chave = f"resposta_{exercicio['id']}"

if exercicio["type"] == "multiple_choice":
    textos = {opcao["id"]: opcao["text"] for opcao in exercicio["options"]}
    resposta = st.radio(
        "Escolha uma alternativa:",
        list(textos),
        index=None,
        format_func=lambda letra: f"{letra}) {textos[letra]}",
        key=chave,
        disabled=finalizado,
    )
else:
    resposta = st.text_input("Sua resposta:", key=chave, disabled=finalizado)

st.caption(f"Tentativas usadas: {st.session_state.tentativas} de {MAX_TENTATIVAS}")

# 5) Botão Responder
if st.button("Responder", key="responder", disabled=finalizado):
    erro_formato = validar_formato(exercicio, resposta)

    if erro_formato:
        st.warning(erro_formato)
    else:
        st.session_state.tentativas += 1
        resultado = avaliar_tentativa(
            exercicio, resposta, st.session_state.tentativas
        )
        st.session_state.resultado = resultado

        if resultado["dica"]:
            st.session_state.dicas.append(resultado["dica"])

        st.rerun()

# 6) Mostrar o resultado
if resultado is not None:
    if resultado["correta"]:
        st.success(resultado["mensagem"])
    else:
        st.error(resultado["mensagem"])

    for numero, dica in enumerate(st.session_state.dicas, start=1):
        st.info(f"Dica {numero}: {dica}")

    if resultado["explicacao"]:
        st.markdown("**Explicação:** " + resultado["explicacao"])

# 7) Botão Próximo exercício (só aparece quando o atual terminou)
if finalizado:
    if st.button("Próximo exercício", key="proximo"):
        st.session_state.indice += 1
        st.session_state.tentativas = 0
        st.session_state.resultado = None
        st.session_state.dicas = []
        st.rerun()
