django-auth-ava
===============

**django-auth-ava** é uma biblioteca Python/Django que fornece modelos concretos, normalizados e de alta performance para autenticação e sincronização de dados do **SUAP** (Sistema Unificado de Administração Pública) no ecossistema do **AVA** (Ambiente Virtual de Aprendizagem).

Construída sobre o `django-suap-auth <https://pypi.org/project/django-suap-auth/>`_, a biblioteca substitui modelos ad-hoc e unifica a estrutura de usuários, e-mails múltiplos, vínculos funcionais e acadêmicos, auditoria de payloads e inlines do Django Admin para projetos como ``painel_ava`` e ``integrador_ava``.

Principais Recursos
-------------------

* **Modelo Concreto de Usuário**: ``Usuario`` estende ``AbstractUser`` com histórico completo via ``django-simple-history`` e campos enriquecidos de identidade SUAP.
* **Múltiplos E-mails Normalizados**: Tabela ``EmailUsuario`` (1xN) para armazenamento de e-mails corporativos, acadêmicos, pessoais, Google Classroom, etc.
* **Vínculos Funcionais e Acadêmicos**: Tabela ``VinculoUsuario`` (1xN) com detalhamento de campus, cargos, cursos e status ativo.
* **Tolerância a Falhas nas APIs do SUAP**: ``AvaUserInfoFetcher`` consulta ``/api/rh/eu/`` (obrigatório) e recupera com resiliência ``/api/rh/meus-vinculos/``, ``/api/rh/meus-dados/``, ``/api/ensino/meus-dados-aluno/`` e ``/api/ensino/periodos/``.
* **Auditoria e Debug 1x1**: ``UsuarioAuditData`` armazena o mapa bruto consolidado dos endpoints em ``last_json``.
* **Registro de Erros**: Tabela ``SincronizacaoErro`` com histórico de falhas de comunicação.
* **Django Admin Integrado**: Inlines prontos para e-mails, vínculos, auditoria e erros com compatibilidade ao ``admintheme-dsgovbr``.

Conteúdo
--------

.. toctree::
   :maxdepth: 2

   installation
   configuration
   models
   fetchers
   admin
   development
