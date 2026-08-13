Desenvolvimento e Contribuição
===============================

Ambiente de Desenvolvimento
---------------------------

1. Clone o repositório e instale as dependências com os pacotes extras de desenvolvimento:

.. code-block:: bash

   git clone git@github.com:suap-ava-suite/djangoapp-auth_ava.git
   cd djangoapp-auth_ava
   pip install -e ".[dev]"

Configuração dos Git Hooks (pre-commit)
---------------------------------------

O projeto utiliza o ``pre-commit`` para garantir a qualidade de código, linting e testes antes de cada envio:

.. code-block:: bash

   # Instala o hook de pré-commit (ruff, formatação, trailing-whitespace)
   pre-commit install

   # Instala o hook de pré-push (execução do pytest com cobertura)
   pre-commit install --hook-type pre-push

Executando Testes e Cobertura
-----------------------------

.. code-block:: bash

   pytest --cov=auth_ava --cov-report=term-missing

Linting e Formatação de Código
------------------------------

.. code-block:: bash

   ruff check .
   ruff format .

Compilação da Documentação
--------------------------

.. code-block:: bash

   python -m sphinx -b html docs docs/_build/html
