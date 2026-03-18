import re
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.nuuvem.com"

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
})


def _baixar_html(url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=5)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def _buscar_link_primeiro_item(nome_jogo: str) -> str | None:
    query = quote_plus(nome_jogo)
    url_busca = f"{BASE_URL}/br-pt/catalog/platforms/pc/search/{query}"
    soup = _baixar_html(url_busca)
    link = soup.select_one('a[href*="/item/"]')
    if not link or not link.has_attr("href"):
        return None
    href = link["href"]
    return href if href.startswith("http") else BASE_URL + href


def _extrair_nome(soup: BeautifulSoup) -> str | None:
    h1 = soup.select_one("h1")
    return h1.get_text(strip=True) if h1 else None


def _extrair_imagem(soup: BeautifulSoup) -> str | None:
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"]
    return None


def _extrair_precos(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    texto = soup.get_text(" ", strip=True)
    matches = re.findall(r"R\$\s*\d[\d\s\.,]*", texto)
    if not matches:
        return None, None
    precos_str = []
    for m in matches:
        raw = m.replace("R$", "").strip()
        raw = re.sub(r"\s+", "", raw)
        precos_str.append(raw)
    valores = []
    for s in precos_str:
        try:
            num = float(s.replace(".", "").replace(",", "."))
            valores.append((s, num))
        except:
            pass
    if not valores:
        return None, None
    positivos = [p for p in valores if p[1] > 0]
    if positivos:
        valores = positivos
    if len(valores) == 1:
        return valores[0][0], valores[0][0]
    return valores[-2][0], valores[-1][0]


def buscar_jogo_nuuvem(nome_jogo: str) -> dict | None:
    url_item = _buscar_link_primeiro_item(nome_jogo)
    if not url_item:
        return None
    soup_item = _baixar_html(url_item)
    nome = _extrair_nome(soup_item)
    imagem = _extrair_imagem(soup_item)
    preco_cheio, preco_atual = _extrair_precos(soup_item)
    return {
        "plataforma": "Nuuvem",
        "nome": nome,
        "url": url_item,
        "preco_atual": preco_atual,
        "preco_cheio": preco_cheio,
        "imagem": imagem,
    }


if __name__ == "__main__":
    termo = input("Digite o nome do jogo: ")
    dados = buscar_jogo_nuuvem(termo)
    if not dados:
        print("Nenhum jogo encontrado na Nuuvem para esse nome.")
    else:
        print("Plataforma:    ", dados["plataforma"])
        print("Nome:          ", dados["nome"])
        print("URL:           ", dados["url"])
        print("Preço atual:   ", f"R$ {dados['preco_atual']}" if dados["preco_atual"] else "N/A")
        print("Preço cheio:   ", f"R$ {dados['preco_cheio']}" if dados["preco_cheio"] else "N/A")
        print("Imagem (URL):  ", dados["imagem"])
