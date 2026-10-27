# CodeTutor — Especificação do Projeto

**Status:** Em desenvolvimento  
**Versão do documento:** 0.1  
**Última atualização:** 26/10/2026

## 1. Visão geral

O CodeTutor é uma aplicação web educacional voltada para estudantes iniciantes em Python. O sistema busca ajudar o estudante a identificar dificuldades, praticar programação por meio de exercícios progressivos e compreender seus erros com o auxílio de dicas e explicações.

A aplicação será desenvolvida em Python, com interface web construída usando Streamlit. O conteúdo pedagógico será armazenado em arquivos JSON, enquanto o histórico de tentativas será registrado em um banco de dados SQLite.

## 2. Problema

Estudantes iniciantes em programação podem ter dificuldade para identificar quais conteúdos precisam revisar, encontrar exercícios adequados ao seu nível e compreender os erros cometidos durante a resolução.

O CodeTutor pretende oferecer uma experiência de estudo organizada, com diagnóstico inicial, prática orientada e acompanhamento do desempenho.

## 3. Objetivos

### 3.1. Objetivo geral

Desenvolver uma aplicação web que auxilie estudantes iniciantes a aprender fundamentos de Python por meio de exercícios organizados, correção automática, dicas progressivas e acompanhamento do desempenho.

### 3.2. Objetivos específicos

- Identificar dificuldades iniciais por meio de um diagnóstico.
- Organizar exercícios por assunto e nível de dificuldade.
- Corrigir automaticamente as respostas dos formatos de exercício suportados.
- Oferecer dicas progressivas antes de apresentar a explicação completa.
- Selecionar exercícios seguintes de acordo com regras pedagógicas definidas.
- Registrar tentativas e acompanhar o desempenho por assunto.
- Avaliar a experiência de uso e os resultados de aprendizagem em um estudo piloto.

## 4. Público-alvo

Estudantes que estão começando a aprender programação em Python e precisam de orientação para praticar, compreender erros e revisar conteúdos fundamentais.

## 5. Escopo do MVP

### 5.1. Funcionalidades incluídas

- Diagnóstico inicial de conhecimentos.
- Banco de exercícios organizado por assunto e dificuldade.
- Questões de múltipla escolha.
- Questões de previsão de saída de código.
- Questões de completar código.
- Questões de resposta curta.
- Correção automática dos formatos implementados.
- Dicas progressivas e explicações das respostas.
- Seleção do próximo exercício por regras programadas.
- Registro das tentativas em SQLite.
- Resumo do desempenho geral e por assunto.
- Material de apoio organizado por conteúdo.
- Interface web responsiva.
- Validação de entradas e tratamento de erros esperados.

### 5.2. Funcionalidades fora do escopo inicial

- Cadastro de usuários e recuperação de senha.
- Execução livre de código enviado pelo estudante.
- Integração com modelos de linguagem ou APIs externas de IA generativa.
- Personalização baseada em estilos de aprendizagem.
- Ranking competitivo e sistemas complexos de gamificação.
- Aplicativo móvel nativo.

## 6. Requisitos funcionais

Os requisitos funcionais descrevem o que o sistema deve fazer.

- **RF01 — Diagnóstico:** permitir que o estudante responda a questões iniciais para identificar conhecimentos e dificuldades.
- **RF02 — Seleção de exercícios:** disponibilizar exercícios filtrados por assunto e nível.
- **RF03 — Apresentação:** exibir o enunciado e os elementos necessários para responder a cada tipo de questão.
- **RF04 — Correção:** avaliar a resposta segundo as regras definidas para o tipo de exercício.
- **RF05 — Dicas:** disponibilizar dicas progressivas quando solicitadas pelo estudante.
- **RF06 — Explicação:** apresentar a resposta esperada e explicar o raciocínio após a tentativa, conforme as regras de feedback.
- **RF07 — Progressão:** selecionar o próximo exercício com base em regras programadas e no desempenho registrado.
- **RF08 — Histórico:** registrar e consultar tentativas, respostas e resultados.
- **RF09 — Desempenho:** apresentar indicadores de aproveitamento geral e por assunto.
- **RF10 — Material de apoio:** permitir que o estudante consulte explicações e exemplos relacionados aos conteúdos.
- **RF11 — Validação:** verificar entradas e dados dos exercícios, tratando erros previsíveis sem interromper indevidamente a aplicação.

## 7. Requisitos não funcionais

Os requisitos não funcionais definem condições de qualidade e funcionamento.

- **RNF01 — Usabilidade:** apresentar navegação clara e adequada a iniciantes.
- **RNF02 — Responsividade:** permitir utilização em navegadores de computadores e dispositivos móveis.
- **RNF03 — Manutenibilidade:** separar interface, lógica pedagógica e persistência de dados em módulos distintos.
- **RNF04 — Confiabilidade:** validar os dados dos exercícios e testar as regras principais do sistema.
- **RNF05 — Privacidade:** coletar apenas os dados necessários ao funcionamento e à avaliação, evitando exposição de informações pessoais.
- **RNF06 — Reprodutibilidade:** documentar a instalação, as dependências e as instruções de execução.
- **RNF07 — Transparência pedagógica:** utilizar regras de seleção e correção que possam ser compreendidas e explicadas pela equipe.

## 8. Arquitetura do sistema

A aplicação será organizada em três camadas principais.

### 8.1. Interface

Arquivo principal: `app.py`

Responsável por apresentar as telas, receber as respostas, controlar a interação com o estudante e exibir os resultados fornecidos pelo núcleo pedagógico.

### 8.2. Núcleo pedagógico

Pasta: `codetutor/`

- `exercicios.py`: carregamento, validação e filtragem dos exercícios.
- `diagnostico.py`: avaliação dos resultados do diagnóstico inicial.
- `tutor.py`: seleção de exercícios, progressão de dificuldade e gerenciamento das dicas.
- `desempenho.py`: cálculo dos indicadores de aproveitamento.
- `historico.py`: registro e consulta das tentativas.
- `__init__.py`: organização do pacote Python.

### 8.3. Dados e persistência

- `data/exercicios/`: arquivos JSON com os exercícios de prática.
- `data/testes/`: questões destinadas ao pré-teste e ao pós-teste.
- `data/historico.db`: banco SQLite criado durante a execução para armazenar tentativas.

Os arquivos JSON conterão o conteúdo pedagógico elaborado pela equipe. O banco SQLite armazenará os registros de utilização do sistema.

## 9. Organização dos dados dos exercícios

Os exercícios serão armazenados em arquivos JSON, preferencialmente separados por assunto.

Cada exercício deverá possuir um identificador único, assunto, nível de dificuldade, tipo, enunciado, resposta esperada, dicas progressivas e explicação final. Campos adicionais poderão ser necessários conforme o formato da questão.

Os tipos previstos são:

- `multiple_choice`: múltipla escolha.
- `predict_output`: previsão da saída de um código.
- `fill_blank`: completar código.
- `short_answer`: resposta curta.

O esquema definitivo dos arquivos JSON deverá ser documentado antes da produção em escala dos exercícios. As regras de correção deverão considerar as particularidades de cada formato.

## 10. Fluxo principal do estudante

1. O estudante acessa a aplicação.
2. Realiza o diagnóstico inicial.
3. Recebe uma orientação inicial baseada no resultado.
4. Escolhe ou inicia uma sequência de exercícios.
5. Responde à questão apresentada.
6. Recebe a correção e pode consultar dicas progressivas.
7. Visualiza a explicação correspondente.
8. O sistema registra a tentativa e atualiza os indicadores de desempenho.
9. O tutor seleciona o próximo exercício conforme as regras definidas.
10. O estudante consulta seu progresso e o material de apoio.

## 11. Testes e validação

Os testes automatizados serão utilizados para verificar o carregamento dos exercícios, a validação de dados, a correção das respostas, as regras de progressão e os cálculos de desempenho.

Também serão realizados testes manuais da interface e dos fluxos completos de utilização.

A avaliação experimental poderá utilizar um pré-teste e um pós-teste com questões equivalentes, respeitando os procedimentos acordados com o orientador. A análise deverá considerar o tamanho da amostra e as limitações do estudo.

A participação de estudantes deverá ser voluntária, com dados tratados de forma anônima sempre que possível e sem impacto na nota acadêmica.

## 12. Tecnologias

- **Python:** linguagem principal.
- **Streamlit:** construção da interface web.
- **JSON:** armazenamento dos exercícios.
- **SQLite:** persistência do histórico.
- **Git e GitHub:** controle de versão e colaboração.
- **unittest:** testes automatizados da lógica.
- **pandas e matplotlib:** análise dos dados experimentais, quando necessária.

## 13. Organização da equipe

A equipe dividirá o trabalho entre desenvolvimento técnico e produção de conteúdo pedagógico.

A frente técnica será responsável pela arquitetura, lógica do tutor, interface, persistência, testes e integração dos módulos.

A frente pedagógica será responsável pela elaboração e revisão dos exercícios, gabaritos, dicas, explicações e materiais de apoio.

As decisões sobre o formato dos dados, as regras de funcionamento e as alterações na especificação deverão ser compartilhadas entre os integrantes.

## 14. Critérios gerais de conclusão

O MVP será considerado funcional quando:

- O aplicativo puder ser iniciado e utilizado em um navegador.
- O diagnóstico inicial puder ser concluído.
- Os exercícios forem carregados e apresentados corretamente.
- Os formatos de questão implementados puderem ser corrigidos.
- As dicas e explicações forem exibidas de acordo com as regras definidas.
- O sistema conseguir selecionar o próximo exercício.
- As tentativas forem registradas e consultadas no SQLite.
- O resumo de desempenho apresentar resultados consistentes.
- Os testes principais forem executados com sucesso.
- A instalação, a execução e a arquitetura estiverem documentadas.

## 15. Decisões pendentes

Os seguintes pontos deverão ser definidos e atualizados durante o desenvolvimento:

- Formato JSON definitivo e exemplos validados.
- Lista final de assuntos conforme o conteúdo estudado pela turma.
- Quantidade final de exercícios e distribuição por nível.
- Regras detalhadas de correção para cada tipo de questão.
- Critérios de seleção do próximo exercício.
- Procedimentos de coleta e análise de dados acordados com o orientador.
