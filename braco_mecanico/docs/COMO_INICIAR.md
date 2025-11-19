# 🚀 Como Iniciar - Guia Completo

## Passo a Passo para Iniciar Tudo

### 📋 Pré-requisitos
- Python 3.8+ instalado
- Node.js instalado (para Node-RED)
- Mosquitto MQTT Broker instalado

---

## 1️⃣ Instalar Dependências Python

```bash
pip install -r requirements.txt
```

**Verificar instalação:**
```bash
python teste_rapido.py
```

Deve mostrar: `✓ Todos os testes básicos passaram!`

---

## 2️⃣ Instalar e Configurar MQTT Broker (Mosquitto)

### Windows:
1. Baixe de: https://mosquitto.org/download/
2. Instale o Mosquitto
3. Inicie o serviço:
   ```powershell
   net start mosquitto
   ```

### Linux:
```bash
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl start mosquitto
sudo systemctl enable mosquitto  # Iniciar automaticamente
```

**Testar se está rodando:**
```bash
# Windows
Get-Service mosquitto

# Linux
sudo systemctl status mosquitto
```

---

## 3️⃣ Instalar Node-RED

### Opção A: Script Automático (Windows)
```bash
instalar_node_red.bat
```

### Opção B: Manual
```bash
npm install -g node-red
npm install -g node-red-dashboard
```

**Verificar instalação:**
```bash
node-red --version
```

---

## 4️⃣ Iniciar Node-RED

```bash
node-red
```

**Acesse:** http://localhost:1880

Você verá a interface do Node-RED.

---

## 5️⃣ Importar Fluxo no Node-RED

1. No Node-RED, clique no **menu (☰)** no canto superior direito
2. Selecione **Importar**
3. Clique em **Selecionar um arquivo para importar**
4. Escolha: `node_red_flow_organizado.json`
5. Clique em **Importar**
6. Clique no botão **Implantar** (vermelho, canto superior direito)

**Resultado:** Você verá dois fluxos:
- Manipulador Planar (esquerda)
- Robô Móvel (direita)

---

## 6️⃣ Testar Conexão MQTT

Em um novo terminal:

```bash
python testar_mqtt.py
```

**Deve mostrar:**
```
✓ Broker MQTT está acessível
✓ Conectado ao broker MQTT
✓ Métricas enviadas com sucesso!
```

**No Node-RED:**
- Os nós MQTT devem ficar com ponto **verde** (conectado)
- Se aparecer mensagens no debug, está funcionando!

---

## 7️⃣ Acessar Dashboard

No navegador, acesse:

**http://localhost:1880/ui**

Você verá duas abas:
- **Manipulador Planar** - Métricas do braço robótico
- **Robô Móvel** - Métricas do robô

---

## 8️⃣ Executar os Sistemas

### Terminal 1: Manipulador Planar
```bash
python exemplo_manipulador.py
```

**O que acontece:**
- Abre visualização 3D do braço robótico
- Braço move para ângulos de referência
- Métricas aparecem no dashboard em tempo real

### Terminal 2: Robô Móvel
```bash
python exemplo_robo_movel.py
```

**O que acontece:**
- Abre visualização 3D do robô
- Robô navega evitando obstáculos
- Métricas aparecem no dashboard em tempo real

---

## 📊 Verificar Dashboard

1. Acesse: http://localhost:1880/ui
2. Clique na aba **"Manipulador Planar"**
   - Veja gráfico de erro
   - Veja gauges atualizando
   - Veja status de estabilização

3. Clique na aba **"Robô Móvel"**
   - Veja gráfico de distância
   - Veja número de colisões
   - Veja métricas atualizando

---

## 🔧 Troubleshooting

### MQTT não conecta
```bash
# Verificar se Mosquitto está rodando
Get-Service mosquitto  # Windows
sudo systemctl status mosquitto  # Linux

# Iniciar se necessário
net start mosquitto  # Windows
sudo systemctl start mosquitto  # Linux
```

### Node-RED não inicia
```bash
# Verificar se Node.js está instalado
node --version

# Reinstalar Node-RED
npm install -g node-red --force
```

### Dashboard não aparece
```bash
# Reinstalar dashboard
npm install -g node-red-dashboard

# Reiniciar Node-RED
# (Ctrl+C para parar, depois node-red novamente)
```

### Python não encontra módulos
```bash
# Reinstalar dependências
pip install -r requirements.txt --upgrade
```

### Visualização não abre
- Certifique-se de que `use_gui=True` nos scripts
- No Linux, pode precisar: `sudo apt-get install python3-opengl`

---

## 📝 Checklist Rápido

- [ ] Python e dependências instaladas
- [ ] Mosquitto instalado e rodando
- [ ] Node-RED instalado
- [ ] Node-RED rodando (porta 1880)
- [ ] Fluxo importado no Node-RED
- [ ] Dashboard acessível (localhost:1880/ui)
- [ ] Teste MQTT passou
- [ ] Scripts Python executando

---

## 🎯 Ordem de Inicialização (Resumo)

1. **Mosquitto** (sempre primeiro)
   ```bash
   net start mosquitto  # Windows
   ```

2. **Node-RED** (segundo)
   ```bash
   node-red
   ```

3. **Importar fluxo** no Node-RED

4. **Testar conexão**
   ```bash
   python testar_mqtt.py
   ```

5. **Executar sistemas**
   ```bash
   python exemplo_manipulador.py
   python exemplo_robo_movel.py
   ```

---

## 🎉 Pronto!

Agora você tem:
- ✅ Broker MQTT rodando
- ✅ Node-RED configurado
- ✅ Dashboard visualizando métricas
- ✅ Sistemas robóticos simulando

**Aproveite!** 🚀

