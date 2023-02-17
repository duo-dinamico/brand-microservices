# Prioridades

- [x] Routes para patch de ~~brand~~, ~~user~~ e ~~categories~~
- [x] Routes para delete de ~~brand~~, ~~user~~ e ~~categories~~
- ~~[ ] Conftest que cria categorias, brands e users devia retornar o que cria para usar em testes que precisam de um atributo~~
- [x] Mudar modelos para adicionar created at, created by, updated at, updated by, deleted at, deleted by
- [x] Mudar secrets para github secrets
- [x] Antes de correr qualquer docker, fazer down primeiro no Makefile
- [x] Complementar as routes preenchendo os timestamps e ownerships de ~~categories~~, ~~brands~~ e ~~users~~
- [x] Mudar respostas para ser sempre um objecto com uma chave com uma lista (mesmo que seja só um) [~~brands~~], [~~categories~~] e [~~users~~]

  ```python
      {"users": [
          {"id": ...,

          }
      ]}
  ```

- ~~ [ ] Em criacao de brands, o id da categoria deve ser um parametero e nao estar no body~~
- [x] Adicionar query show_deleted
- [ ] Adicionar routes para ir buscar so 1 categoria, 1 brand e 1 user
- [ ] Adicionar mais testes e testar a validacao
- [x] Acrescentar branch develop. Criar regras para merge em develop e merge em main
- [ ] Corrigir bug em POST LOGIN User (linha 240)
- [ ] Adicionar localização das lojas no Brands
- [ ] Diferenciar marcas Portuguesas de estrangeiras.
- [ ] Resposta do Brand com a Categoria como objecto
- [ ] Respostas gerais dos \_by User como objecto.
- [ ] Validação das passwords e usernames.
- [x] Limitar PR de develop para main.
- [ ] Criar as pastas de dados dos Docker no servidor.

# Futuro

- [ ] Confirmação de registo por email.
- [ ] Roles para Users.

# Tidyup

- [ ] Rever o tutorial do fastapi no site deles especialmente a parte avancada
- [ ] Refazer o README
- [ ] Criar o contributing guide
- [ ] Discutir uma maneira de manter os packages actualizados
- [ ] Criar utilizador para o docker nao criar pastas com root
- [ ] Melhorar validacao de pydantic

# Manutencao

- [ ] Criar conta em Linode e Github a pagantes
