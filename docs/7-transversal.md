# 7. Padrão transversal: observabilidade

Aplicamos a observabilidade da seção 18.5 do livro, com dois dos três sinais que ela descreve, o log estruturado e o ponto de saúde.

## Onde está no código

- [sira/observabilidade.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/0cc5a9c67182dcbdf6af9b70c05d636c53f22656/sira/observabilidade.py#L18-L67): o `FormatoJson` escreve cada linha de log como um objeto JSON com momento, nível, evento e o id da requisição. O middleware de `medir_requisicoes` gera esse id, ou usa o que veio no cabeçalho `x-request-id`, guarda o id em um `ContextVar` durante a requisição, devolve no cabeçalho da resposta e, no fim, registra método, rota, status e duração. Erro não tratado sai no mesmo log, com o rastro da exceção.
- [sira/risco/cronometro.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/0cc5a9c67182dcbdf6af9b70c05d636c53f22656/sira/risco/cronometro.py#L19-L26): cada estimativa registra o próprio tempo e a versão do modelo no mesmo log, e por causa do `ContextVar` a linha sai com o id da requisição que a gerou.
- [sira/app.py](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/0cc5a9c67182dcbdf6af9b70c05d636c53f22656/sira/app.py#L44-L52): `GET /saude` confere se o banco responde e informa a versão do modelo carregado.

```python
def _registrar(requisicao: Request, status: int, inicio: float) -> None:
    # só método, rota e status: o corpo e os parâmetros podem trazer dado de paciente (RNF02)
    dados = {
        "metodo": requisicao.method,
        "rota": requisicao.url.path,
        "status": status,
        "duracao_ms": round((perf_counter() - inicio) * 1000, 1),
    }
    log.info("requisicao", extra={"dados": dados})
```

Um cadastro gera duas linhas como estas, ligadas pelo mesmo id:

```json
{"momento": "2026-11-21 20:14:03,512", "nivel": "INFO", "evento": "estimativa", "requisicao": "a609ceabc30f", "duracao_ms": 20.8, "versao_modelo": "2.0"}
{"momento": "2026-11-21 20:14:03,516", "nivel": "INFO", "evento": "requisicao", "requisicao": "a609ceabc30f", "metodo": "POST", "rota": "/casos", "status": 201, "duracao_ms": 28.1}
```

## Por que este sistema precisa dele

O RNF03 fixa limites de tempo, 1 segundo para a estimativa e 3 segundos para a lista. Sem a duração de cada requisição e de cada estimativa registrada, não há como saber se os limites valem com o sistema em uso, nem separar o tempo gasto no modelo do tempo gasto no banco.

O RNF09 pede rastreabilidade das predições. O caso já guarda quem cadastrou, quando e com qual versão do modelo, e o log mostra a mesma versão na linha da estimativa, com o id que liga essa linha à requisição que a pediu.

Os casos são dados de saúde (RNF02), então o log não pode virar um vazamento. Como ele é estruturado, os campos são fixos: método, rota, status e duração, sem corpo e sem parâmetros, o que o teste [test_requisicao_vira_uma_linha_json_sem_o_corpo](https://github.com/Mendes2719/grupo-01-pas-sira-tb/blob/0cc5a9c67182dcbdf6af9b70c05d636c53f22656/tests/test_observabilidade.py#L22-L35) confere.

Por fim, o sistema roda como um processo só, que carrega o modelo na subida (ADR 0007). O `/saude` é o que quem opera consulta para saber se a instância está de pé e se ela carregou a versão esperada do modelo depois de um retreino.

Não aplicamos rastreamento distribuído: com um processo só, a requisição não atravessa outros serviços, e o id no log basta para seguir o caminho dela.
