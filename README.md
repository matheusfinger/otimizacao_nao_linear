# Otimização Não-Linear

Ferramenta com interface gráfica desenvolvida em grupo para a disciplina de Programação Não-Linear. O sistema permite realizar análises e otimizações de funções matemáticas, incluindo a parametrização de funções multivariáveis em funções unidimensionais para busca de passo ótimo (α).

## Funcionalidades Atuais
* Parametrização simbólica de funções multivariáveis $\phi(\alpha) = f(x_0 + \alpha d)$.
* Método da Bisseção, Newton e Condições de Wolfe.
* Interface gráfica limpa e responsiva construída com PyQt5.

## Pré-requisitos

Para rodar este projeto, você precisa ter o **Python 3** (ou superior) instalado na sua máquina.

## Instalação

Clone o repositório e, na pasta raiz do projeto, instale as dependências necessárias utilizando o arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Execução

Para executar, use o código abaixo:

```bash
python3 principal.py
```