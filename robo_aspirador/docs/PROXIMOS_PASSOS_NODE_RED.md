# Próximos Passos no Node-RED

## ✅ Você já fez:
- [x] Configurou HTTP In (POST /robo-data)
- [x] Nome: "Recebe Dados do Robô"

## 🔄 Agora faça:

### PASSO 1: Salvar o Nó HTTP In
1. **Clique em "Feito"** (botão vermelho no painel direito)
2. O nó será salvo e você voltará à área de trabalho

### PASSO 2: Adicionar Nó Debug
1. **Na paleta esquerda**, procure por "debug"
2. **Arraste** o nó "debug" para a área de trabalho (ao lado do HTTP In)
3. **Clique duas vezes** no nó debug (ou deixe padrão)

### PASSO 3: Conectar os Nós
1. **Passe o mouse** sobre o nó "Recebe Dados do Robô" (HTTP In)
2. Você verá um **ponto azul** aparecer na lateral direita
3. **Clique e arraste** desse ponto até o nó "debug"
4. Uma **linha azul** conectará os dois nós

### PASSO 4: Ativar Debug
1. **No painel direito**, procure pelo ícone de **🐛 (bug)**
2. **Clique** para ativar (ficará destacado quando ativo)
3. Isso mostrará os dados recebidos

### PASSO 5: Adicionar HTTP Response (Opcional)
1. **Na paleta esquerda**, procure por "http response"
2. **Arraste** para a área de trabalho
3. **Conecte** após o debug: `[HTTP In] → [Debug] → [HTTP Response]`
4. **Clique duas vezes** no http response
5. **Status Code**: `200`
6. **Clique em "Feito"**

### PASSO 6: Deploy (CRÍTICO!)
1. **No canto superior direito**, procure o botão **"implementar"** (vermelho)
2. **Clique em "implementar"**
3. Aguarde confirmação
4. O flow está ativo!

## ✅ Flow Final Deve Estar Assim:

```
[Recebe Dados do Robô (HTTP In)]
    ↓ (linha azul)
[debug]
    ↓ (linha azul)
[http response] (opcional)
```

## 🧪 Testar Agora

Após fazer Deploy, teste:

```bash
python tests/test-node-red.py
```

**Você deve ver:**
- Dados aparecendo no painel Debug (lado direito)
- Mensagem de sucesso no teste

## 📊 O que você verá no Debug

Quando o robô enviar dados, aparecerá algo como:

```json
{
  "timestamp": "2024-...",
  "type": "metrics",
  "data": {
    "coverage_percentage": 4.3,
    "total_time": 0.0,
    ...
  }
}
```

## ⚠️ Lembre-se

- **Sempre faça Deploy** após mudanças!
- O debug deve estar **ativado** (ícone bug)
- Os nós devem estar **conectados** (linhas azuis)

## 🎯 Resumo Rápido

1. ✅ HTTP In configurado (você já fez!)
2. ➡️ Clique em "Feito"
3. ➡️ Adicione Debug e conecte
4. ➡️ Ative debug (ícone bug)
5. ➡️ **CLIQUE EM "IMPLEMENTAR"** (Deploy)

**Pronto para testar!** 🚀

