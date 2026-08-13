Fetchers e Sincronização
=========================

O ``AvaUserInfoFetcher`` gerencia a consulta aos múltiplos endpoints do SUAP com estratégia de tolerância a falhas.

Endpoints Consumidos
--------------------

1. ``/api/rh/eu/`` (**Obrigatório**):
   Contém a identificação primária, nomes, documentos e campus do usuário. Se falhar, a autenticação é interrompida com erro explicativo.

2. ``/api/rh/meus-vinculos/`` (**Tolerante a Falhas**):
   Retorna a listagem de todos os vínculos (servidor, aluno, prestador) e seus detalhamentos.

3. ``/api/rh/meus-dados/`` (**Tolerante a Falhas**):
   Retorna dados funcionais detalhados de servidores do IFRN.

4. ``/api/ensino/meus-dados-aluno/`` (**Tolerante a Falhas**):
   Retorna dados acadêmicos de discentes (curso, matriz, IRA, ingresso).

5. ``/api/ensino/periodos/`` (**Tolerante a Falhas**):
   Retorna a listagem de semestres letivos do aluno.

Resiliência e Registro
----------------------

Caso algum endpoint secundário retorne código HTTP de erro (como 403 para alunos tentando acessar dados de RH ou servidores tentando acessar dados de aluno) ou falha de rede:

* O erro é registrado na tabela ``SincronizacaoErro``.
* O payload de resposta é registrado no campo ``last_json`` do ``UsuarioAuditData``.
* O login do usuário é concluído normalmente com os dados disponíveis.
