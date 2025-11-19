# 🚀 COMO INICIAR - Resumo Visual

## ⚡ Início Rápido (5 minutos)

### Opção 1: Script Automático (Windows)
```bash
iniciar_tudo.bat
```

### Opção 2: Manual

#### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 2️⃣ Iniciar Mosquitto (MQTT)
```bash
net start mosquitto
```

#### 3️⃣ Iniciar Node-RED
```bash
node-red
```
👉 Acesse: http://localhost:1880

#### 4️⃣ Importar Fluxo no Node-RED
- Menu (☰) → **Importar**
- Arquivo: `node_red_flow_organizado.json`
- Clique em **Implantar**

#### 5️⃣ Executar Sistemas
```bash
# Terminal 1
python exemplo_manipulador.py

# Terminal 2  
python exemplo_robo_movel.py
```

#### 6️⃣ Ver Dashboard
👉 http://localhost:1880/ui

---

## 📊 Fluxo Visual

```
┌─────────────────────────────────────────┐
│  1. Mosquitto (MQTT Broker)            │
│     net start mosquitto                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. Node-RED                           │
│     node-red                            │
│     → http://localhost:1880            │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. Importar Fluxo                      │
│     node_red_flow_organizado.json       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  4. Executar Sistemas                  │
│     python exemplo_manipulador.py      │
│     python exemplo_robo_movel.py       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  5. Dashboard                           │
│     http://localhost:1880/ui            │
│     → Ver métricas em tempo real        │
└─────────────────────────────────────────┘
```

---

## 📁 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `COMO_INICIAR.md` | Guia completo passo a passo |
| `INICIO_RAPIDO.md` | Resumo rápido |
| `iniciar_tudo.bat` | Script automático Windows |
| `node_red_flow_organizado.json` | Fluxo Node-RED (importar) |
| `testar_mqtt.py` | Testar conexão MQTT |

---

## ✅ Checklist

- [ ] Python instalado
- [ ] `pip install -r requirements.txt`
- [ ] Mosquitto instalado e rodando
- [ ] Node-RED instalado
- [ ] Node-RED rodando (porta 1880)
- [ ] Fluxo importado
- [ ] Dashboard acessível

---

## 🆘 Problemas?

**MQTT não conecta?**
```bash
net start mosquitto
python testar_mqtt.py
```

**Node-RED não inicia?**
```bash
npm install -g node-red node-red-dashboard
```

**Ver guia completo:** `COMO_INICIAR.md`

