Modelos de Dados
================

O ``django-auth-ava`` implementa uma estrutura normalizada de dados:

Usuario
-------

Modelo concreto que estende ``AbstractUser`` com dados de identificação do SUAP:

* ``username``: IFRN-id / matrícula do SUAP.
* ``nome_registro``: Nome civil completo.
* ``nome_social``: Nome social (se cadastrado).
* ``nome_usual``: Nome de apresentação / preferencial.
* ``tipo_usuario``: Enum com escolhas (``Servidor (Docente)``, ``Servidor (Técnico-Administrativo)``, ``Aluno``, ``Prestador de Serviço``, ``Desconhecido``).
* ``cpf``, ``rg``, ``passaporte``, ``data_nascimento``, ``sexo``, ``naturalidade``.
* ``campus``: Sigla do campus principal.
* ``first_login``: Registro temporal do primeiro acesso.
* ``settings``: Campo JSON para preferências de tema e acessibilidade.

EmailUsuario (1xN)
------------------

Tabela normalizada que armazena múltiplos e-mails por usuário:

* ``tipo``: Tipo do e-mail (``preferencial``, ``pessoal``, ``corporativo``, ``google_classroom``, ``academico``, ``escolar``, etc.).
* ``email``: Endereço de e-mail.

VinculoUsuario (1xN)
--------------------

Tabela normalizada de vínculos funcionais e acadêmicos:

* ``suap_id``: Identificador do vínculo no SUAP.
* ``identificador``: Matrícula específica do vínculo.
* ``tipo``: ``servidor``, ``aluno``, ``prestador_servico``.
* ``campus``: Campus de lotação ou do curso.
* ``cargo``, ``categoria``, ``curso``, ``modalidade``, ``nivel_ensino``, ``situacao``, ``ativo``.
* ``detalhamento``: JSON complementar com metadados do vínculo.

UsuarioAuditData (1x1)
----------------------

Tabela de auditoria vinculada 1x1 ao usuário:

* ``last_json``: Dicionário completo com as respostas brutas dos endpoints consultados durante o login.
* ``atualizado_em``: Data e hora da última sincronização.

SincronizacaoErro (1xN)
-----------------------

Registro de falhas ocorridas na consulta de endpoints secundários:

* ``endpoint``: URL do endpoint (ex: ``/api/ensino/meus-dados-aluno/``).
* ``status_code``: Código HTTP retornado (ex: 403, 404, 500).
* ``mensagem_erro``: Detalhamento do erro ou exceção.
