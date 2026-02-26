# gog_teste_simples.py
import requests

CATALOG_URL = "https://catalog.gog.com/v1/catalog"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.gog.com/en/games",
}


def testar_busca_gog(nome: str, limite: int = 10):
    params = {
        "limit": limite,
        "order": "asc:externalProductId",
        # deixa o tipo bem amplo pra não filtrar demais
        "productType": "in:game,pack,dlc,extras",
        # em vez de query=like:... usa search direto
        "search": nome,
        # você pode comentar essas linhas se desconfiar de região:
        "countryCode": "BR",
        "currencyCode": "BRL",
        "locale": "pt-BR",
    }

    try:
        resp = requests.get(
            CATALOG_URL,
            params=params,
            headers=HEADERS,
            timeout=20,
        )
    except requests.RequestException as e:
        print(f"[GOG] Erro de rede no catálogo: {e}")
        return

    print(f"[GOG] CATALOG status: {resp.status_code}")
    # só pra ver a URL real usada
    print("[GOG] URL usada:", resp.url)

    if resp.status_code != 200:
        print("[GOG] Resposta não OK. Trecho da resposta:")
        print(resp.text[:400])
        return

    try:
        data = resp.json()
    except ValueError:
        print("[GOG] Erro ao decodificar JSON. Trecho da resposta:")
        print(resp.text[:400])
        return

    products = data.get("products") or []
    product_count = data.get("productCount")
    print(f"[GOG] Quantidade products: {len(products)} (productCount={product_count})")

    if not products:
        print("Nenhum produto retornado pelo catálogo para esse nome.")
        return

    print("\nPrimeiros resultados:\n")
    for p in products[:5]:
        print("ID      :", p.get("id"))
        print("Título  :", p.get("title"))
        print("Tipo    :", p.get("productType"))
        print("Cover V :", p.get("coverVertical"))
        print("Cover H :", p.get("coverHorizontal"))
        print("-" * 40)


if __name__ == "__main__":
    termo = input("Nome do jogo (GOG): ")
    testar_busca_gog(termo)
