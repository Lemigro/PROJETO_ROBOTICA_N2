"""Teste simples do endpoint Node-RED"""
import requests
import json

url = "http://127.0.0.1:1880/robo-data"

# Dados de teste simples
dados_teste = {
    "timestamp": "2024-01-01T12:00:00",
    "type": "test",
    "data": {"mensagem": "teste de conexao"}
}

print("Testando conexao com Node-RED...")
print(f"URL: {url}")
print(f"Dados: {json.dumps(dados_teste, indent=2)}")
print()

try:
    # Timeout curto - só para verificar se consegue enviar
    # Não importa se não recebe resposta, o importante é enviar
    response = requests.post(url, json=dados_teste, timeout=2)
    print(f"[OK] Dados enviados com sucesso!")
    print(f"Status Code: {response.status_code}")
    if response.text:
        print(f"Resposta: {response.text[:200]}")
    else:
        print("(Sem resposta - isso e normal se nao tiver http response)")
except requests.exceptions.ConnectionError:
    print("[ERRO] Nao foi possivel conectar ao Node-RED")
    print("   Verifique se o Node-RED esta rodando")
    print("   Execute: node-red")
except requests.exceptions.Timeout:
    print("[AVISO] Timeout ao receber resposta")
    print("   Mas os dados podem ter sido enviados!")
    print("   Verifique o painel de debug do Node-RED")
    print("   Se os dados aparecerem la, esta funcionando!")
    print()
    print("   Dica: Adicione um nó 'http response' no final do flow")
    print("   Ou remova o nó 'http' se nao precisar de resposta")
except Exception as e:
    print(f"[ERRO] {type(e).__name__}: {e}")

