from concurrent.futures import ThreadPoolExecutor, as_completed

from scraping_epic.scraping_epic import scrape_epic_game
from scraping_nintendo.scraping_nintendo import scrape_nintendo_game
from scraping_playstation.scraping_playstation import scrape_playstation_game
from scraping_gog.scraping_gog import scrape_gog_game
from scraping_steam.scraping_games import buscar_jogo_exato
from scraping_xbox.scraping_xbox import scrape_xbox_game
from scraping_nuvem.scraping_nuvem import buscar_jogo_nuuvem
from scraping_itch.scraping_itch import scrape_itch_game

def scrape_steam_wrapper(nome_jogo):
    res = buscar_jogo_exato(nome_jogo)
    if not res: return None
    return {
        "nome": res.get("nome"),
        "preco_atual": res.get("preco_atual"),
        "preco_original": res.get("preco_original"),
        "imagem": None,
        "link": res.get("url")
    }


def executar_scraper(loja, funcao, nome_jogo):
    try:
        resultado = funcao(nome_jogo)

        if not resultado:
            return loja, {
                "nome": None,
                "preco_atual": None,
                "preco_original": None,
                "imagem": None,
                "link": None,
                "erro": "Nenhum resultado encontrado"
            }

        if "erro" not in resultado:
            resultado["erro"] = None

        return loja, resultado

    except Exception as e:
        return loja, {
            "nome": None,
            "preco_atual": None,
            "preco_original": None,
            "imagem": None,
            "link": None,
            "erro": str(e)
        }


def buscar_em_todas_lojas(nome_jogo):
    scrapers = {
        "Steam": scrape_steam_wrapper,
        "Epic": scrape_epic_game,
        "GOG": scrape_gog_game,
        "PlayStation": scrape_playstation_game,
        "Nintendo": scrape_nintendo_game,
        "Xbox": scrape_xbox_game,
        "Nuuvem": buscar_jogo_nuuvem,
        "Itch.io": scrape_itch_game
    }

    resultados = {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(executar_scraper, loja, funcao, nome_jogo): loja
            for loja, funcao in scrapers.items()
        }

        for future in as_completed(futures):
            loja, resultado = future.result()
            resultados[loja] = resultado

    return resultados


def mostrar_resultados(resultados):
    print("\n========= RESULTADO =========\n")

    for loja, dados in resultados.items():
        print(f"===== {loja} =====")
        print("Nome:", dados.get("nome"))
        print("Preço atual:", dados.get("preco_atual"))
        print("Preço original:", dados.get("preco_original"))
        print("Imagem:", dados.get("imagem"))
        print("Link:", dados.get("link"))
        print("Erro:", dados.get("erro"))
        print()


if __name__ == "__main__":
    jogo = input("Digite o nome do jogo: ").strip()
    resultados = buscar_em_todas_lojas(jogo)
    mostrar_resultados(resultados)