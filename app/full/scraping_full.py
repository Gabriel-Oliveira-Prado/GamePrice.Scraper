# scraping_full.py
from scraping_games import buscar_jogo_exato
from scraping_img import pegar_imagem_jogo

def pegar_info_completa(termo):
    dados_jogo = buscar_jogo_exato(termo)
    if not dados_jogo:
        return None

    imagem = pegar_imagem_jogo(termo)

    # junta tudo num dict só
    dados_jogo["imagem"] = imagem
    return dados_jogo


if __name__ == "__main__":
    termo = input("Nome exato do jogo: ")
    info = pegar_info_completa(termo)

    if not info:
        print("Nenhum jogo encontrado com esse nome exato.")
    else:
        print("\nResultado completo:\n")
        print(f"Nome: {info['nome']}")
        print(f"Preço atual: {info['preco_atual']}")
        print(f"Preço original: {info['preco_original']}")
        print(f"URL: {info['url']}")
        print(f"Imagem: {info['imagem']}")
