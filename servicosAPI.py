import json  # manipula dados no formato json
import urllib.request  # Permite abrir e ler URLs (endereços web)
import urllib.error  # Gerencia as exceções (erros) ao tentar acessar uma URL
import urllib.parse  # Permite codificar textos para usar em URLs

# ========== CONSTANTES ==========
# API da Wikipedia em Português para buscar resumos de páginas
API_WIKIPEDIA_URL = "https://pt.wikipedia.org/api/rest_v1/page/summary/"
# URL da Action API para busca inteligente (OpenSearch)
API_BUSCA_URL = "https://pt.wikipedia.org/w/api.php"


# ========== API EXTERNA (Wikipedia) ==========

def buscar_resumo_wikipedia(assunto):
    # ENTRADA: o assunto/nome da foto (ex: "Revolucao Francesa")
    # PROCESSAMENTO: busca o termo inteligente na Wikipedia e consome a API para pegar um resumo
    # SAÍDA: retorna o texto de resumo ou uma mensagem de erro
    try:
        # ETAPA 1: Usa o OpenSearch da Action API para encontrar o título oficial correto (ex: "pitagoras" -> "Pitágoras")
        parametros_busca = urllib.parse.urlencode({
            "action": "opensearch",
            "search": assunto,
            "limit": 1,
            "format": "json"
        })
        url_busca = f"{API_BUSCA_URL}?{parametros_busca}"

        requisicao_busca = urllib.request.Request(url_busca, headers={'User-Agent': 'CameraJovi_StudyAI/1.0'})
        with urllib.request.urlopen(requisicao_busca, timeout=5) as resposta_busca:
            resultado_busca = json.load(resposta_busca)
            titulos = resultado_busca[1]
            if not titulos:
                return "Assunto nao encontrado na base de dados da Wikipedia. Verifique se o nome da foto esta escrito corretamente (ex: 'Mitose', 'Guerra Fria')."
            titulo_oficial = titulos[0]

        # ETAPA 2: Formata a URL com o título oficial e consome a API de resumo
        termo_formatado = urllib.parse.quote(titulo_oficial)  # Converte espaços e acentos para formato web
        url = API_WIKIPEDIA_URL + termo_formatado

        # A Wikipedia exige um cabeçalho User-Agent para saber quem está acessando
        requisicao = urllib.request.Request(url, headers={'User-Agent': 'CameraJovi_StudyAI/1.0'})
        with urllib.request.urlopen(requisicao, timeout=5) as resposta:
            dados = json.load(resposta)
            # Retorna a chave "extract", que contém o resumo em texto puro
            return dados.get("extract", "Resumo nao disponivel para este termo.")

    except urllib.error.HTTPError as erro:
        if erro.code == 404:
            return "Assunto nao encontrado na base de dados da Wikipedia. Verifique se o nome da foto esta escrito corretamente (ex: 'Mitose', 'Guerra Fria')."
        return f"Erro ao acessar a Wikipedia (Codigo: {erro.code})."
    except (OSError, ValueError, TypeError):
        return "AVISO: Nao foi possivel conectar a Wikipedia. Verifique sua internet."