"""
Usa o modelo treinado para estimar o risco de abandono de um paciente.

Como biblioteca (a API usa assim):
    from prever import Preditor
    Preditor().prever({"idade": 34, "sexo": "Masculino", ...})

Pela linha de comando (a partir da raiz do projeto):
    python api/prever.py                                 pergunta campo a campo
    python api/prever.py exemplos/paciente_exemplo.json  le os dados de um arquivo

Campos obrigatorios: os que quase nunca ficaram vazios no historico.
Nos demais, vazio = ignorado (como o codigo 9 do SINAN).

Cada fator vem com dois numeros: "peso" e a contribuicao em pontos
percentuais. O peso e a contribuicao SHAP em log-odds, escala do
modelo. Os pontos percentuais sao essa contribuicao traduzida para a
probabilidade -- quanto ela cairia se o fator fosse retirado da conta.
E o numero que faz sentido mostrar ao profissional de saude.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

PASTA = Path(__file__).resolve().parent.parent / "modelo"

ESCOLARIDADE = ["Analfabeto", "1a a 4a serie incompleta", "4a serie completa",
                "5a a 8a serie incompleta", "Fundamental completo", "Medio incompleto",
                "Medio completo", "Superior incompleto", "Superior completo"]

# as sete da contagem de vulnerabilidades. IMIGRANTE saiu do modelo,
# mas continua no formulario porque entra na contagem.
VULNERABILIDADES = ["USA_ALCOOL", "USA_DROGAS", "TABAGISTA", "TEM_DOENCA_MENTAL",
                    "SITUACAO_DE_RUA", "PRIVADO_LIBERDADE", "IMIGRANTE"]

# variaveis do modelo que vem do mesmo campo do formulario sao somadas
# na explicacao: o usuario informou um municipio, nao "VOL" e "TX"
GRUPO = {"VOL_MUN_RES": "municipio_residencia", "TX_MUN_RES": "municipio_residencia",
         "UF_RESIDENCIA": "municipio_residencia",
         "ANO": "data_notificacao", "MES_NOTIFICACAO": "data_notificacao",
         "DIAS_DIAG_TRAT": "data_inicio_tratamento"}

ROTULO = {
    "tipo_entrada": "Tipo de entrada", "idade": "Idade", "sexo": "Sexo",
    "raca_cor": "Raca/cor", "escolaridade": "Escolaridade",
    "forma_clinica": "Forma clinica", "sorologia_hiv": "Sorologia para HIV",
    "baciloscopia_escarro": "Baciloscopia de escarro", "cultura_escarro": "Cultura de escarro",
    "teste_molecular": "Teste molecular", "raio_x_torax": "Raio-X de torax",
    "usa_alcool": "Uso de alcool", "usa_drogas": "Uso de drogas ilicitas",
    "tabagista": "Tabagismo", "tem_doenca_mental": "Doenca mental",
    "situacao_de_rua": "Situacao de rua", "privado_liberdade": "Privado de liberdade",
    "qtd_contatos": "Numero de contatos", "qtd_vulnerabilidades": "Numero de vulnerabilidades",
    "municipio_residencia": "Municipio de residencia",
    "data_notificacao": "Data da notificacao",
    "data_inicio_tratamento": "Tempo entre diagnostico e inicio do tratamento",
}


# variaveis do modelo que saem de cada campo (padrao: o proprio nome)
ORIGEM = {"data_notificacao": ["ANO", "MES_NOTIFICACAO"], "data_diagnostico": ["DIAS_DIAG_TRAT"],
          "data_inicio_tratamento": ["DIAS_DIAG_TRAT"],
          "municipio_residencia": ["UF_RESIDENCIA", "TX_MUN_RES", "VOL_MUN_RES"],
          "imigrante": []}
LIMITE_VAZIO = 0.01


def _data(v):
    if v in (None, "") or isinstance(v, date):
        return v or None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError(f"data invalida: '{v}' (use AAAA-MM-DD ou DD/MM/AAAA)")


def _numero(nome, v):
    if v in (None, ""):
        return np.nan
    try:
        return float(v)
    except (TypeError, ValueError):
        raise ValueError(f"{nome}: '{v}' nao e numero")


class Preditor:
    def __init__(self, pasta=PASTA):
        self.meta = json.loads((Path(pasta) / "metadados.json").read_text(encoding="utf-8"))
        self.booster = xgb.Booster()
        self.booster.load_model(Path(pasta) / "modelo.json")
        cat = self.meta["categorias"]
        self.ufs = set(cat["UF_RESIDENCIA"])

        # campos do formulario, na ordem em que fazem sentido para quem preenche
        self.campos = {
            "data_notificacao": {"tipo": "data", "descricao": "Data da notificacao"},
            "data_diagnostico": {"tipo": "data", "descricao": "Data do diagnostico"},
            "data_inicio_tratamento": {"tipo": "data", "descricao": "Data de inicio do tratamento"},
            "municipio_residencia": {"tipo": "municipio", "descricao": "Municipio de residencia (codigo IBGE)"},
            "idade": {"tipo": "numero", "descricao": "Idade"},
            "escolaridade": {"tipo": "escolaridade", "descricao": "Escolaridade", "valores": ESCOLARIDADE},
            "qtd_contatos": {"tipo": "numero", "descricao": "Numero de contatos identificados"},
        }
        for c, valores in cat.items():
            if not c.startswith("UF_"):
                self.campos[c.lower()] = {"tipo": "categoria", "descricao": ROTULO.get(c.lower(), c),
                                          "valores": valores}
        self.campos["imigrante"] = {"tipo": "categoria", "descricao": "Imigrante",
                                    "valores": ["Nao", "Sim"]}

        # Campo que quase nunca ficou vazio no historico (< 1%) e obrigatorio:
        # o modelo nao aprendeu o que a ausencia dele significa, e o palpite
        # nesse caso e arbitrario (tipo de entrada vazio jogava qualquer
        # paciente para risco muito alto). Nos demais, vazio = ignorado,
        # que no historico e informacao real (associado a mais abandono).
        vazio = self.meta["vazio_no_treino"]
        for nome, info in self.campos.items():
            cols = ORIGEM.get(nome, [nome.upper()])
            info["obrigatorio"] = bool(cols) and max(vazio[c] for c in cols) < LIMITE_VAZIO

    def _municipio(self, v, avisos):
        if v in (None, ""):
            return None
        cod = str(v).strip()[:6]
        if not (cod.isdigit() and len(cod) == 6 and cod[:2] in self.ufs):
            raise ValueError(f"municipio_residencia: '{v}' nao e um codigo IBGE de municipio valido")
        if cod not in self.meta["municipio"]["taxa"]:
            avisos.append("municipio sem casos no historico: usada a taxa nacional")
        return cod

    def _montar(self, d, avisos):
        d = {k.lower(): (None if v == "" else v) for k, v in d.items()}
        desconhecidos = set(d) - set(self.campos)
        if desconhecidos:
            raise ValueError(f"campos desconhecidos: {sorted(desconhecidos)}")
        faltando = [n for n, i in self.campos.items() if i["obrigatorio"] and d.get(n) is None]
        if faltando:
            raise ValueError(f"campos obrigatorios nao informados: {faltando}")
        vazios = [n for n, i in self.campos.items() if not i["obrigatorio"] and d.get(n) is None]
        if vazios:
            avisos.append(f"{len(vazios)} campo(s) nao informado(s). No historico, fichas "
                          "incompletas se associam a mais abandono, o que eleva a estimativa.")

        x = {}
        dn, dd, dt = (_data(d.get(k)) for k in
                      ("data_notificacao", "data_diagnostico", "data_inicio_tratamento"))
        # anos posteriores ao treino sao tratados pelas arvores como o ultimo ano visto
        x["ANO"] = (dn or date.today()).year
        x["MES_NOTIFICACAO"] = dn.month if dn else np.nan
        dias = (dt - dd).days if (dt and dd) else np.nan
        # mesma regra do tratamento: fora de -30 a 365 dias e erro de registro
        x["DIAS_DIAG_TRAT"] = dias if -30 <= dias <= 365 else np.nan

        x["IDADE"] = _numero("idade", d.get("idade"))
        x["QTD_CONTATOS"] = _numero("qtd_contatos", d.get("qtd_contatos"))
        esc = d.get("escolaridade")
        x["ESCOLARIDADE"] = ESCOLARIDADE.index(esc) if esc in ESCOLARIDADE else _numero("escolaridade", esc)

        for nome, info in self.campos.items():
            if info["tipo"] == "categoria" and d.get(nome) is not None and d[nome] not in info["valores"]:
                raise ValueError(f"{nome}: '{d[nome]}' invalido. Opcoes: {info['valores']}")
        for c in self.meta["categorias"]:
            if not c.startswith("UF_"):
                x[c] = d.get(c.lower())

        res = self._municipio(d.get("municipio_residencia"), avisos)
        t = self.meta["municipio"]
        x["UF_RESIDENCIA"] = res[:2] if res else None
        x["VOL_MUN_RES"] = t["volume"].get(res, 0) if res else np.nan
        x["TX_MUN_RES"] = t["taxa"].get(res, t["media"]) if res else np.nan

        # mesma regra do tratamento: nenhum dos sete informado = contagem nula
        vul = [d.get(c.lower()) for c in VULNERABILIDADES]
        x["QTD_VULNERABILIDADES"] = (np.nan if all(v is None for v in vul)
                                     else sum(v == "Sim" for v in vul))

        # valores mostrados ao lado de cada fator na explicacao
        valores = {k: (v.isoformat() if isinstance(v, date) else v) for k, v in d.items()}
        valores["qtd_vulnerabilidades"] = x["QTD_VULNERABILIDADES"]
        valores["data_inicio_tratamento"] = (f"{x['DIAS_DIAG_TRAT']:.0f} dias"
                                             if not np.isnan(x["DIAS_DIAG_TRAT"]) else None)
        return x, valores

    def prever_lote(self, lista, n_fatores=5):
        avisos = [[] for _ in lista]
        montados = [self._montar(d, a) for d, a in zip(lista, avisos)]
        X = pd.DataFrame([x for x, _ in montados])[self.meta["variaveis"]]
        for c in self.meta["numericas"]:
            X[c] = pd.to_numeric(X[c]).astype(float)
        for c, valores in self.meta["categorias"].items():
            X[c] = pd.Categorical(X[c], categories=valores)

        dm = xgb.DMatrix(X, enable_categorical=True)
        probs = self.booster.predict(dm)
        # a ultima coluna e o ponto de partida do modelo, igual para todos
        bruto = self.booster.predict(dm, pred_contribs=True)
        contribs, partida = bruto[:, :-1], float(bruto[0, -1])
        cortes = self.meta["faixas"]
        q = self.meta["percentis"]

        saida = []
        for prob, contrib, (_, valores), av in zip(probs, contribs, montados, avisos):
            grupos = {}
            for var, c in zip(self.meta["variaveis"], contrib):
                g = GRUPO.get(var, var.lower())
                grupos[g] = grupos.get(g, 0.0) + float(c)
            # converte o peso (log-odds) em pontos percentuais: quanto a
            # probabilidade cairia se este fator fosse retirado da conta
            total = float(np.log(prob / (1 - prob)))
            pp = {g: float(prob - 1 / (1 + np.exp(-(total - c)))) * 100 for g, c in grupos.items()}
            fatores = sorted(grupos.items(), key=lambda kv: -abs(pp[kv[0]]))[:n_fatores]
            faixa = "Baixo"
            for nome, corte in cortes:
                if prob >= corte:
                    faixa = nome
            saida.append({
                "probabilidade": round(float(prob), 4),
                "faixa": faixa,
                "percentil": int(round(np.interp(prob, q, np.linspace(0, 100, len(q))))),
                "probabilidade_base": round(float(1 / (1 + np.exp(-partida))), 4),
                "fatores": [{"fator": ROTULO.get(g, g),
                             "valor": valores.get(g) if valores.get(g) is not None else "nao informado",
                             "efeito": "aumenta" if c > 0 else "reduz",
                             "pontos_percentuais": round(pp[g], 1),
                             "peso": round(c, 3)} for g, c in fatores],
                "avisos": av,
            })
        return saida

    def prever(self, dados, n_fatores=5):
        return self.prever_lote([dados], n_fatores)[0]


def _perguntar(campos):
    dados = {}
    print("Campos com * sao obrigatorios. Nos demais, em branco = ignorado.\n")
    for nome, info in campos.items():
        marca = " *" if info["obrigatorio"] else ""
        opcoes = info.get("valores")
        while True:
            if opcoes:
                print(info["descricao"] + marca)
                for i, o in enumerate(opcoes, 1):
                    print(f"  {i}. {o}")
                r = input("  > ").strip()
            else:
                r = input(f"{info['descricao']}{marca}: ").strip()
            if r or not info["obrigatorio"]:
                break
        if r:
            dados[nome] = opcoes[int(r) - 1] if opcoes else r
    return dados


if __name__ == "__main__":
    p = Preditor()
    if len(sys.argv) > 1:
        dados = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    else:
        dados = _perguntar(p.campos)

    r = p.prever(dados)
    print(f"\nProbabilidade estimada de abandono: {r['probabilidade']:.1%}")
    print(f"Faixa de risco: {r['faixa']} (risco maior que {r['percentil']}% dos pacientes)")
    print(f"\nPartindo de {r['probabilidade_base']:.1%}, o ponto de partida do modelo,")
    print("os fatores que mais pesaram foram:")
    for f in r["fatores"]:
        print(f"  {f['pontos_percentuais']:+6.1f} p.p.  {f['fator']}: {f['valor']}")
    print("\n(p.p. = quanto a probabilidade cairia sem aquele fator;")
    print(" os valores nao somam o total, porque a escala nao e linear)")
    for a in r["avisos"]:
        print(f"\nAviso: {a}")
