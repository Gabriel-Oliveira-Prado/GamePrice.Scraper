from scraping_xbox.scraping_xbox import scrape_xbox_game
from scraping_epic.scraping_epic import scrape_epic_game
from scraping_nintendo.scraping_nintendo import scrape_nintendo_game
from scraping_playstation.scraping_playstation import scrape_playstation_game
from scraping_gog.scraping_gog import scrape_gog_game
from scraping_nuvem.scraping_nuvem import buscar_jogo_nuuvem
from scraping_steam.scraping_games import buscar_jogo_exato
from scraping_steam.scraping_img import pegar_imagem_jogo


def normalizar(texto):
    if not texto:
        return ""
    return " ".join(texto.lower().strip().split())


def nome_exato(nome_buscado, nome_resultado):
    return normalizar(nome_buscado) == normalizar(nome_resultado)


def padronizar_resultado(resultado, plataforma):
    if not resultado:
        return None

    return {
        "plataforma": plataforma,
        "nome": resultado.get("nome"),
        "preco_atual": resultado.get("preco_atual"),
        "preco_original": resultado.get("preco_original", resultado.get("preco_cheio")),
        "imagem": resultado.get("imagem"),
        "link": resultado.get("link", resultado.get("url"))
    }


def processar_xbox(nome_jogo):
    resultado = scrape_xbox_game(nome_jogo)
    resultado = padronizar_resultado(resultado, "Xbox")

    if not resultado or not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def processar_epic(nome_jogo):
    resultado = scrape_epic_game(nome_jogo)
    resultado = padronizar_resultado(resultado, "Epic Games")

    if not resultado or not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def processar_nintendo(nome_jogo):
    resultado = scrape_nintendo_game(nome_jogo)
    resultado = padronizar_resultado(resultado, "Nintendo")

    if not resultado or not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def processar_playstation(nome_jogo):
    resultado = scrape_playstation_game(nome_jogo)
    resultado = padronizar_resultado(resultado, "PlayStation")

    if not resultado or not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def processar_gog(nome_jogo):
    resultado = scrape_gog_game(nome_jogo)
    resultado = padronizar_resultado(resultado, "GOG")

    if not resultado or not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def processar_nuuvem(nome_jogo):
    resultado = buscar_jogo_nuuvem(nome_jogo)
    resultado = padronizar_resultado(resultado, "Nuuvem")

    if not resultado or not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def processar_steam(nome_jogo):
    dados = buscar_jogo_exato(nome_jogo)
    if not dados:
        return None

    imagem = pegar_imagem_jogo(nome_jogo)

    resultado = {
        "plataforma": "Steam",
        "nome": dados.get("nome"),
        "preco_atual": dados.get("preco_atual"),
        "preco_original": dados.get("preco_original"),
        "imagem": imagem,
        "link": dados.get("url")
    }

    if not nome_exato(nome_jogo, resultado["nome"]):
        return None

    return resultado


def mostrar_resultado(resultado):
    print("\n==============================")
    print("Plataforma:", resultado.get("plataforma"))
    print("Nome:", resultado.get("nome"))
    print("Preço atual:", resultado.get("preco_atual"))
    print("Preço original:", resultado.get("preco_original"))
    print("Imagem:", resultado.get("imagem"))
    print("Link:", resultado.get("link"))


def main():
    nome_jogo = input("Digite o nome do jogo: ").strip()

    funcoes = [
        processar_xbox,
        processar_epic,
        processar_nintendo,
        processar_playstation,
        processar_gog,
        processar_nuuvem,
        processar_steam
    ]

    resultados = []

    for func in funcoes:
        try:
            resultado = func(nome_jogo)
            if resultado:
                resultados.append(resultado)
        except Exception as e:
            print(f"Erro em {func.__name__}: {e}")

    if not resultados:
        print("\nNenhum jogo encontrado com nome exato em nenhuma plataforma.")
        return

    print("\nRESULTADOS ENCONTRADOS:")
    for resultado in resultados:
        mostrar_resultado(resultado)


if __name__ == "__main__":
    main()
