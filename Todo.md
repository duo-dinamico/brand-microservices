# Prioridades

- [x] Routes para patch de ~~brand~~, ~~user~~ e ~~categories~~
- [x] Routes para delete de ~~brand~~, ~~user~~ e ~~categories~~
- ~~[ ] Conftest que cria categorias, brands e users devia retornar o que cria para usar em testes que precisam de um atributo~~
- [x] Mudar modelos para adicionar created at, created by, updated at, updated by, deleted at, deleted by
- [x] Mudar secrets para github secrets
- [x] Antes de correr qualquer docker, fazer down primeiro no Makefile
- [ ] Complementar as routes preenchendo os timestamps e ownerships de ~~categories~~, brands e users
- [ ] Mudar respostas parea ser sempre um objecto com uma chave com uma lista (mesmo que seja só um)
- [ ] Em criacao de brands, o id da categoria deve ser um parametero e nao estar no body

  ```python
      {"users": [
          {"id": ...,

          }
      ]}
  ```

- [ ] Adicionar mais testes e testar a validacao
- [ ] Adicionar query show_deleted

# Tidyup

- [ ] Rever o tutorial do fastapi no site deles especialmente a parte avancada
- [ ] Refazer o README
- [ ] Criar o contributing guide
- [ ] Discutir uma maneira de manter os packages actualizados
- [ ] Criar utilizador para o docker nao criar pastas com root
- [ ] Melhorar validacao de pydantic

# Manutencao

- [ ] Criar conta em Linode e Github a pagantes
