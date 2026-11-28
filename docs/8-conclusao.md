# 8. Conclusão

## O que funcionou

Isolar o preditor do PI em vez de reescrevê-lo foi a decisão que mais economizou trabalho. O teste de caracterização entrou no primeiro PR, antes de qualquer mudança, e conferiu durante todo o trabalho que a estimativa continuava a mesma, enquanto o resto do sistema nunca precisou conhecer o XGBoost nem o formato de resposta do PI.

As portas pagaram o próprio custo quando o JWT precisou sair: a troca pela sessão no banco ficou no adaptador do módulo de acesso e em uma linha de `sira/app.py`, e o decorador que mede a estimativa entrou do mesmo jeito, sem mexer no adaptador nem no serviço. A refatoração da lista antes dos indicadores também deu certo, porque com o Builder os indicadores ficaram com seis linhas e conferem com a lista por construção.

Ter o ruff, o pytest e o CI desde o primeiro PR fez com que nenhum PR entrasse no main com erro de lint ou teste quebrado, e o teste de arquitetura deixou a fronteira entre os módulos verificada, e não só desenhada.

## O que não funcionou

O ADR 0005 foi escrito seguindo o documento do PI, que previa JWT, sem a gente reler o critério de aceitação do logout no RF09. O problema só apareceu quando o logout foi implementado, e a decisão teve de ser substituída pelo ADR 0006, com retrabalho.

O SQLite atende o volume de um município, mas aceita uma escrita por vez e não deixa subir uma segunda instância, então não serve para uma implantação estadual. A tabela de sessões também acumula as sessões vencidas até alguém apagá-las.

O teste de arquitetura confere o módulo de onde vem cada importação, mas não o nome importado de dentro dele: `from sira.risco import http` passaria, mesmo com `http` sendo interno. Hoje só o `app.py` faz isso, de propósito, mas a verificação não pegaria o mesmo erro em outro lugar.

Sem a interface web, o fluxo foi validado só pela documentação interativa do FastAPI, o que não mostra se as telas previstas vão precisar de algo que a API ainda não oferece.

## O que faríamos diferente

Leríamos os critérios de aceitação de cada requisito antes de escrever o ADR correspondente, o que teria evitado o JWT. Também escreveríamos desde o começo um teste de ponta a ponta pela API, com o modelo real, cobrindo login, cadastro e lista, e combinaríamos com quem vai construir a interface o contrato das rotas antes de implementar a lista e os indicadores.

## Referências

ABREU, Douglas Henrique Siqueira. **Estilos Arquiteturais de Software: guia de consulta**. Campinas: PUC-Campinas, 2026. Material da disciplina Padrões e Arquitetura de Software.

SHVETS, Alexander. **Padrões de projeto**. Refactoring.Guru, 2026. Disponível em: https://refactoring.guru/pt-br/design-patterns. Páginas usadas: [Adapter](https://refactoring.guru/pt-br/design-patterns/adapter), [Builder](https://refactoring.guru/pt-br/design-patterns/builder) e [Decorator](https://refactoring.guru/pt-br/design-patterns/decorator). Acesso em: nov. 2026.

SHVETS, Alexander. **Refatoração**. Refactoring.Guru, 2026. Disponível em: https://refactoring.guru/pt-br/refactoring. Páginas usadas: [Long Parameter List](https://refactoring.guru/pt-br/smells/long-parameter-list), [Data Clumps](https://refactoring.guru/pt-br/smells/data-clumps), [Duplicate Code](https://refactoring.guru/pt-br/smells/duplicate-code), [Primitive Obsession](https://refactoring.guru/pt-br/smells/primitive-obsession), [Introduce Parameter Object](https://refactoring.guru/pt-br/introduce-parameter-object), [Extract Class](https://refactoring.guru/pt-br/extract-class) e [Replace Type Code with Class](https://refactoring.guru/pt-br/replace-type-code-with-class). Acesso em: nov. 2026.

COCKBURN, Alistair. **Hexagonal Architecture**. 2005. Disponível em: https://alistair.cockburn.us/hexagonal-architecture/. Acesso em: nov. 2026.

NYGARD, Michael. **Documenting Architecture Decisions**. Cognitect, 2011. Disponível em: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions. Acesso em: nov. 2026.

BROWN, Simon. **The C4 model for visualising software architecture**. [s. d.]. Disponível em: https://c4model.com/. Acesso em: nov. 2026.

FEATHERS, Michael. **Working Effectively with Legacy Code**. Upper Saddle River: Prentice Hall, 2004. Disponível em: https://www.informit.com/store/working-effectively-with-legacy-code-9780131177055. Acesso em: nov. 2026.

OPENTELEMETRY. **Signals**. [s. d.]. Disponível em: https://opentelemetry.io/docs/concepts/signals/. Acesso em: nov. 2026.

OWASP. **Password Storage Cheat Sheet**. [s. d.]. Disponível em: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html. Acesso em: nov. 2026.

BRASIL. **Lei nº 13.709, de 14 de agosto de 2018**. Lei Geral de Proteção de Dados Pessoais. 2018. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. Acesso em: nov. 2026.

ASTRAL. **Ruff**. 2026. Disponível em: https://docs.astral.sh/ruff/. Acesso em: nov. 2026.

RAMÍREZ, Sebastián. **FastAPI**. 2026. Disponível em: https://fastapi.tiangolo.com/. Acesso em: nov. 2026.

MERMAID. **C4 Diagrams**. [s. d.]. Disponível em: https://mermaid.js.org/syntax/c4.html. Acesso em: nov. 2026.

CONVENTIONAL COMMITS. **Conventional Commits 1.0.0**. 2019. Disponível em: https://www.conventionalcommits.org/pt-br/v1.0.0/. Acesso em: nov. 2026.
