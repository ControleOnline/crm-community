#!/usr/bin/env python3
import sys
import re
import os

# Este script:
# - recebe um ou mais caminhos (arquivos e/ou diretórios), todos SEM aspas mesmo se tiverem espaços
# - reconstrói os caminhos internamente (como se estivessem entre aspas)
# - para diretórios, percorre recursivamente
# - processa apenas arquivos .js e .jsx
# - PROCURA linhas do tipo:
#     const {getters: ordersGetters, actions: ordersActions} = getStore('orders');
#     const {actions: invoiceActions, getters} = getStore('invoice');
#     const {actions, getters: invoiceGetters} = getStore('invoice');
# - e SUBSTITUI por:
#     const ordersStore = useStores(state => state.orders);
#     const ordersGetters = ordersStore.getters;
#     const ordersActions = ordersStore.actions;
#
#     const invoiceStore = useStores(state => state.invoice);
#     const invoiceActions = invoiceStore.actions;
#     const getters = invoiceStore.getters;
#
#     const invoiceStore = useStores(state => state.invoice);
#     const actions = invoiceStore.actions;
#     const invoiceGetters = invoiceStore.getters;
#
# - NÃO cria backup.

DECL_REGEX = re.compile(
    r"""
    ^(?P<indent>\s*)                # indentação inicial
    (?P<decl>const|let|var)         # const/let/var
    \s*
    \{
        (?P<inside>[^}]*)           # conteúdo entre { e }
    \}
    \s*=\s*
    getStore
    \s*\(\s*
        (?P<quote>['"])
        (?P<store_name>[^'"]+)      # nome do store: orders, invoice, etc.
        (?P=quote)
    \s*\)
    \s*;
?   \s*$
    """,
    re.VERBOSE,
)

# Captura itens com e sem alias:
#   getters: invoiceGetters
#   getters
INSIDE_REGEX = re.compile(
    r"""
    (?P<prop>\w+)                # ex: getters, actions
    (?:\s*:\s*(?P<alias>\w+))?   # opcional: ": alias"
    """,
    re.VERBOSE,
)


def gerar_linhas_novas(indent: str, store_name: str, inside: str):
    """
    Gera as novas linhas que substituem a linha original de getStore.
    """
    store_var = f"{store_name}Store"

    # Lista de (prop, alias_ou_vazio)
    props = INSIDE_REGEX.findall(inside)

    linhas = []

    # Linha principal da store
    linhas.append(
        f"{indent}const {store_var} = useStores(state => state.{store_name});\n"
    )

    # Uma const para cada item
    for prop, alias in props:
        var_name = alias if alias else prop
        linhas.append(f"{indent}const {var_name} = {store_var}.{prop};\n")

    return linhas


def aplicar_em_arquivo(caminho_arquivo: str):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except UnicodeDecodeError:
        with open(caminho_arquivo, "r", encoding="latin-1") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: \"{caminho_arquivo}\"")
        return False, 0

    novas_linhas = []
    alterou = False
    total_matches = 0

    for linha in linhas:
        m = DECL_REGEX.match(linha)
        if not m:
            # linha permanece igual
            novas_linhas.append(linha)
            continue

        # Encontrou uma linha compatível -> substitui
        alterou = True
        total_matches += 1

        indent = m.group("indent") or ""
        store_name = m.group("store_name")
        inside = m.group("inside")

        bloco_novo = gerar_linhas_novas(indent, store_name, inside)

        # Adiciona o bloco novo no lugar da linha original
        novas_linhas.extend(bloco_novo)

    if not alterou:
        # Nada para fazer nesse arquivo
        return False, 0

    # Grava arquivo alterado (sem backup)
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.writelines(novas_linhas)
    except Exception as e:
        print(f"[ERRO] Ao gravar arquivo \"{caminho_arquivo}\": {e}")
        return False, 0

    print(f"[OK] \"{caminho_arquivo}\" - {total_matches} ocorrência(s) alterada(s)")
    return True, total_matches


def iterar_arquivos(caminho: str):
    """
    Para um caminho:
      - se for arquivo .js ou .jsx, yield caminho
      - se for diretório, percorre recursivamente e yield cada .js/.jsx
      - se não existir, avisa
    """
    if not os.path.exists(caminho):
        print(f"[AVISO] Caminho não encontrado: \"{caminho}\"")
        return

    if os.path.isfile(caminho):
        ext = os.path.splitext(caminho)[1].lower()
        if ext in (".js", ".jsx"):
            yield os.path.abspath(caminho)
        else:
            return
    else:
        for root, dirs, files in os.walk(caminho):
            for nome in files:
                ext = os.path.splitext(nome)[1].lower()
                if ext not in (".js", ".jsx"):
                    continue
                yield os.path.abspath(os.path.join(root, nome))


def reconstruir_caminhos_sem_aspas(argv_slice):
    """
    Recebe sys.argv[1:] (sem o nome do script), onde cada parte pode ser:
      - pedaço de um caminho com espaço
      - ou um caminho inteiro sem espaço

    Estratégia:
      - Um novo caminho começa quando:
        * a palavra começa com "/"  (caminho absoluto)
        * OU é a primeira palavra e NÃO começa com "-" (para suportar "./algo", "../x", etc.)
      - Senão, a palavra é anexada ao caminho atual com um espaço.
    """
    if not argv_slice:
        return []

    caminhos = []
    atual = []

    for i, parte in enumerate(argv_slice):
        inicia_novo = False

        if parte.startswith("/"):
            inicia_novo = True
        elif i == 0:
            if not parte.startswith("-"):
                inicia_novo = True

        if inicia_novo:
            if atual:
                caminhos.append(" ".join(atual))
            atual = [parte]
        else:
            atual.append(parte)

    if atual:
        caminhos.append(" ".join(atual))

    return caminhos


def main():
    if len(sys.argv) < 2:
        print("Uso: ./applyTroca.py caminho/para/arquivo_ou_diretorio [...outros]")
        print("Ex.: ./applyTroca.py /Users/alemac/Controle Online/proj /tmp/Outro dir")
        sys.exit(1)

    argv_partes = sys.argv[1:]
    caminhos = reconstruir_caminhos_sem_aspas(argv_partes)

    arquivos_processados = set()
    total_arquivos_alterados = 0
    total_ocorrencias = 0

    for caminho in caminhos:
        for arquivo in iterar_arquivos(caminho):
            if arquivo in arquivos_processados:
                continue
            arquivos_processados.add(arquivo)

            alterou, ocorrencias = aplicar_em_arquivo(arquivo)
            if alterou:
                total_arquivos_alterados += 1
                total_ocorrencias += ocorrencias

    print(f"\nTotal de arquivos alterados: {total_arquivos_alterados}")
    print(f"Total de ocorrências alteradas: {total_ocorrencias}")


if __name__ == "__main__":
    main()