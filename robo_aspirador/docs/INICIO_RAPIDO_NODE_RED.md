# Início Rápido: Node-RED

Guia rápido para começar a usar Node-RED em 5 minutos.

## ⚡ Passos Rápidos

### 1. Verificar Instalação

```bash
node-red --version
```

Se não estiver instalado:
```bash
npm install -g node-red
npm install -g node-red-dashboard
```

### 2. Iniciar Node-RED

```bash
node-red
```

Ou use o script:
```bash
scripts\iniciar-node-red.bat
```

### 3. Acessar Interface

Abra: **http://localhost:1880**

### 4. Importar Flow Completo (Recomendado)

1. Menu (☰) → **Import**
2. Selecione: `node-red/node-red-flow-completo-windows.json`
3. Clique em **Import**
4. Clique em **Deploy** (botão vermelho)

**OU** criar flow mínimo:

1. Arraste `http in` → Configure: URL `/robo-data`, Method `POST`
2. Arraste `debug` → Conecte ao `http in`
3. Clique em **Deploy**

### 5. Ver Dashboard

Acesse: **http://localhost:1880/ui**

### 6. Testar

```bash
python tests/test-node-red.py
```

Você deve ver os dados no painel Debug e no Dashboard!

---

## ✅ Pronto!

Agora seu Node-RED está configurado e funcionando.

**Próximos passos:**
- Veja o [Guia Completo](NODE_RED_GUIA_COMPLETO.md) para recursos avançados
- Veja o [Passo a Passo Completo](CONFIGURAR_NODE_RED_PASSO_A_PASSO.md) para configuração detalhada
- Execute o projeto: `python main.py --execution 1`

---

## 🆘 Problemas?

- **Node-RED não inicia?** → Verifique se a porta 1880 está livre
- **Dados não chegam?** → Verifique se fez Deploy e se o endpoint está correto
- **Dashboard não aparece?** → Instale: `npm install -g node-red-dashboard`
- **Erro de instalação?** → Execute como Administrador

Para mais detalhes, consulte:
- [Configurar Node-RED Passo a Passo](CONFIGURAR_NODE_RED_PASSO_A_PASSO.md)
- [Guia Completo](NODE_RED_GUIA_COMPLETO.md)

