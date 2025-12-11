#!/usr/bin/env python3
import sys
import os
import re

def encontrar_getstore_em_arquivo(caminho_arquivo, regex):
    """Retorna a contagem de matches de getStore no arquivo."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except UnicodeDecodeError:
        # tenta latin-1 como fallback
        try:
            with open(caminho_arquivo, 'r', encoding='latin-1') as f:
                conteudo = f.read()
        except Exception as e:
            print(f"[AVISO] Não foi possível ler o arquivo (encoding): {caminho_arquivo} - {e}")
            return 0
    except Exception as e:
        print(f"[AVISO] Erro ao ler o arquivo: {caminho_arquivo} - {e}")
        return 0

    matches = regex.findall(conteudo)
    return len(matches)

def percorrer_diretorio(raiz):
    # Regex simples para encontrar getStore('algo') ou getStore("algo")
    padrao = r"getStore\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    regex = re.compile(padrao)

    total_geral = 0
    arquivos_com_ocorrencia = []

    for dirpath, dirnames, filenames in os.walk(raiz):
        for nome in filenames:
            # Filtra apenas arquivos .js (e .jsx, se quiser)
            if nome.endswith(".js") or nome.endswith(".jsx"):
                caminho_completo = os.path.join(dirpath, nome)
                qtd = encontrar_getstore_em_arquivo(caminho_completo, regex)
                if qtd > 0:
                    arquivos_com_ocorrencia.append((caminho_completo, qtd))
                    total_geral += qtd

    return arquivos_com_ocorrencia, total_geral

def main():
    if len(sys.argv) != 2:
        print("Uso: python contar_getstore.py /caminho/para/diretorio")
        sys.exit(1)

    raiz = sys.argv[1]
    if not os.path.isdir(raiz):
        print(f"Erro: '{raiz}' não é um diretório válido.")
        sys.exit(1)

    arquivos, total = percorrer_diretorio(raiz)

    if not arquivos:
        print("Nenhuma ocorrência de getStore encontrada.")
        return

    print("Ocorrências de getStore por arquivo:\n")
    for caminho, qtd in arquivos:
        print(f"{caminho}: {qtd}")

    print("\nResumo:")
    print(f"Total de arquivos com getStore: {len(arquivos)}")
    print(f"Total de ocorrências de getStore: {total}")

if __name__ == "__main__":
    main()