# ⚡ Início Rápido - 5 Minutos

## 🎯 Passos Essenciais

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar Mosquitto (MQTT)
```bash
# Windows
net start mosquitto

# Linux
sudo systemctl start mosquitto
```

### 3. Iniciar Node-RED
```bash
node-red
```
Acesse: http://localhost:1880

### 4. Importar Fluxo
- Menu (☰) → Importar
- Selecione: `node_red_flow_organizado.json`
- Clique em **Implantar**

### 5. Executar Sistemas
```bash
# Terminal 1
python exemplo_manipulador.py

# Terminal 2
python exemplo_robo_movel.py
```

### 6. Ver Dashboard
Acesse: http://localhost:1880/ui

---

## 🚀 Script Automático (Windows)

```bash
iniciar_tudo.bat
```

Este script:
- ✅ Verifica Python
- ✅ Instala dependências
- ✅ Inicia Mosquitto
- ✅ Inicia Node-RED
- ✅ Testa conexão MQTT

---

## 📋 Checklist

- [ ] Python instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Mosquitto instalado e rodando
- [ ] Node-RED instalado e rodando
- [ ] Fluxo importado no Node-RED
- [ ] Dashboard acessível

---

## 🆘 Problemas Comuns

**MQTT não conecta?**
```bash
net start mosquitto  # Windows
```

**Node-RED não inicia?**
```bash
npm install -g node-red node-red-dashboard
```

**Python não encontra módulos?**
```bash
pip install -r requirements.txt --upgrade
```

---

## 📚 Documentação Completa

Veja `COMO_INICIAR.md` para guia detalhado.
