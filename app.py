import base64
import os
from collections import Counter
from pathlib import Path

import streamlit as st

from codetutor import nuvem
from codetutor.exercicios import carregar_exercicios, ordenar_exercicios
from codetutor.historico import (
    CAMINHO_PADRAO,
    listar_historico,
    para_csv,
    registrar_tentativa,
)
from codetutor.tutor import (
    MAX_TENTATIVAS,
    avaliar_tentativa,
    proximo_indice,
    validar_formato,
)

RAIZ = Path(__file__).parent
PASTA_EXERCICIOS = RAIZ / "data" / "exercicios"
PASTA_ASSETS = RAIZ / "assets"
# CODETUTOR_DB permite trocar o banco (usado nos testes). Sem ela, usa data/historico.db
CAMINHO_BANCO = os.environ.get("CODETUTOR_DB", CAMINHO_PADRAO)


def segredo(nome):
    """Lê um valor de st.secrets. Devolve None se não existir (ex.: rodando local)."""
    try:
        return st.secrets.get(nome)
    except Exception:
        return None


URL_NUVEM = segredo("SUPABASE_URL")
CHAVE_NUVEM = segredo("SUPABASE_KEY")
USA_NUVEM = bool(URL_NUVEM and CHAVE_NUVEM)


def historico_completo():
    """Todo o histórico: da nuvem se configurada e acessível, senão o local."""
    if USA_NUVEM:
        linhas = nuvem.listar_tentativas(URL_NUVEM, CHAVE_NUVEM)
        if linhas is not None:
            return linhas
    return listar_historico(CAMINHO_BANCO)


def historico_do_participante(codigo):
    """Histórico de um participante (nuvem se possível, senão local)."""
    if USA_NUVEM:
        linhas = nuvem.listar_tentativas(URL_NUVEM, CHAVE_NUVEM, codigo)
        if linhas is not None:
            return linhas
    return listar_historico(CAMINHO_BANCO, codigo)


def mascote_html(largura):
    """Devolve o mascote como <img>. Embutir em base64 evita depender de caminho de arquivo."""
    svg = (PASTA_ASSETS / "mascote.svg").read_bytes()
    codigo = base64.b64encode(svg).decode()
    return f'<img src="data:image/svg+xml;base64,{codigo}" width="{largura}">'


st.set_page_config(
    page_title="CodeTutor",
    page_icon=str(PASTA_ASSETS / "icone.png"),
    layout="centered",
)

# Cabeçalho: mascote + nome com degradê (HTML/CSS simples, o Streamlit permite com unsafe_allow_html)
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:4px;">
        {mascote_html(72)}
        <div>
            <div style="font-size:2.4rem; font-weight:800; line-height:1.1;
                        background:linear-gradient(90deg,#7C5CFA,#34D399);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                CodeTutor
            </div>
            <div style="color:#A9ADC1;">
                Aprenda Python na prática: resolva, receba dicas e entenda seus erros.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1) Carregar o banco de exercícios
try:
    exercicios = ordenar_exercicios(carregar_exercicios(PASTA_EXERCICIOS))
except ValueError as erro:
    st.error("O banco de exercícios tem problemas. Avise quem editou os arquivos.")
    st.code(str(erro))
    st.stop()

if not exercicios:
    st.warning("Nenhum exercício encontrado em data/exercicios.")
    st.stop()

# 2) Barra lateral: como funciona e um resumo do banco (útil para conferir o trabalho de quem escreve os exercícios)
with st.sidebar:
    st.markdown(mascote_html(90), unsafe_allow_html=True)

    participante = st.text_input(
        "Código do participante",
        value="anonimo",
        max_chars=30,
        help="Use o código que o pesquisador te passar. Não escreva seu nome.",
    ).strip() or "anonimo"

    st.header("Como funciona")
    st.write(
        f"Você tem até {MAX_TENTATIVAS} tentativas por exercício. "
        "A cada erro, uma dica nova aparece. No fim, você vê a explicação."
    )

    with st.expander("Banco de exercícios"):
        st.write(f"Total: {len(exercicios)}")
        contagem = Counter((ex["topic"], ex["level"]) for ex in exercicios)
        for assunto in sorted({ex["topic"] for ex in exercicios}):
            por_nivel = [contagem[(assunto, nivel)] for nivel in (1, 2, 3)]
            st.write(
                f"{assunto}: {sum(por_nivel)} "
                f"(níveis 1, 2, 3: {por_nivel[0]}, {por_nivel[1]}, {por_nivel[2]})"
            )

    # Área do pesquisador: só aparece se existir a senha configurada (st.secrets).
    # Sem isso, qualquer visitante do site público poderia baixar o histórico de todos.
    senha_correta = segredo("SENHA_PESQUISADOR")

    if senha_correta:
        with st.expander("Área do pesquisador"):
            senha = st.text_input("Senha", type="password")
            if senha == senha_correta:
                st.download_button(
                    "Baixar histórico (CSV)",
                    data=para_csv(historico_completo()),
                    file_name="historico_codetutor.csv",
                    mime="text/csv",
                )

# 3) Memória da sessão: sobrevive aos cliques, ao contrário das variáveis comuns
# Quando a pessoa abre o app (ou troca o código), retomamos do primeiro exercício
# que ela ainda não concluiu, olhando o histórico.
if st.session_state.get("dono") != participante:
    anterior = proximo_indice(exercicios, historico_do_participante(participante))
    st.session_state.dono = participante
    st.session_state.indice = len(exercicios) if anterior is None else anterior
    st.session_state.tentativas = 0
    st.session_state.resultado = None
    st.session_state.dicas = []
    st.session_state.aviso_nuvem = False

if st.session_state.indice >= len(exercicios):
    st.success("Você concluiu todos os exercícios do banco. Parabéns!")
    st.stop()

posicao = st.session_state.indice
exercicio = exercicios[posicao]
resultado = st.session_state.resultado
finalizado = resultado is not None and resultado["finalizado"]

# 4) O cartão do exercício
with st.container(border=True):
    st.caption(
        f"Exercício {posicao + 1} de {len(exercicios)} | "
        f"Assunto: {exercicio['topic']} | Nível {exercicio['level']} de 3"
    )
    st.markdown(exercicio["statement"])

    if "code" in exercicio:
        st.code("\n".join(exercicio["code"]), language="python")

    # Campo de resposta (a chave inclui o id para cada exercício ter o seu campo)
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

    st.progress(
        st.session_state.tentativas / MAX_TENTATIVAS,
        text=f"Tentativas usadas: {st.session_state.tentativas} de {MAX_TENTATIVAS}",
    )

    # Botão Responder
    if st.button("Responder", key="responder", type="primary", disabled=finalizado):
        erro_formato = validar_formato(exercicio, resposta)

        if erro_formato:
            st.warning(erro_formato)
        else:
            st.session_state.tentativas += 1
            resultado = avaliar_tentativa(
                exercicio, resposta, st.session_state.tentativas
            )
            st.session_state.resultado = resultado

            registro = registrar_tentativa(
                CAMINHO_BANCO,
                participante,
                exercicio,
                st.session_state.tentativas,
                resultado,
            )
            if USA_NUVEM and not nuvem.enviar_tentativa(URL_NUVEM, CHAVE_NUVEM, registro):
                st.session_state.aviso_nuvem = True

            if resultado["dica"]:
                st.session_state.dicas.append(resultado["dica"])

            st.rerun()

    if st.session_state.get("aviso_nuvem"):
        st.caption("Aviso: não consegui salvar esta tentativa na nuvem. Avise o pesquisador.")

    # Resultado
    if resultado is not None:
        if resultado["correta"]:
            st.success(resultado["mensagem"])
        else:
            st.error(resultado["mensagem"])

        for numero, dica in enumerate(st.session_state.dicas, start=1):
            st.info(f"Dica {numero}: {dica}")

        if resultado["explicacao"]:
            st.markdown("**Explicação:** " + resultado["explicacao"])

    # Botão Próximo exercício (só aparece quando o atual terminou)
    if finalizado:
        if st.button("Próximo exercício", key="proximo"):
            st.session_state.indice += 1
            st.session_state.tentativas = 0
            st.session_state.resultado = None
            st.session_state.dicas = []
            st.rerun()
