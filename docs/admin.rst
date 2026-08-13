Django Admin
============

O ``django-auth-ava`` disponibiliza configurações completas para o Django Admin:

Inlines
-------

* **EmailUsuarioInline**: Exibe e gerencia a lista tabular de e-mails do usuário.
* **VinculoUsuarioInline**: Exibe os vínculos funcionais e acadêmicos em blocos organizados.
* **UsuarioAuditDataInline**: Exibe o ``last_json`` consolidado em modo de visualização somente-leitura.
* **SincronizacaoErroInline**: Exibe os registros de falhas ocorridas na comunicação com os endpoints secundários.

Compatibilidade Visual
----------------------

Os modelos e inlines são totalmente compatíveis com o tema ``admintheme-dsgovbr`` e temas padrão do Django.
