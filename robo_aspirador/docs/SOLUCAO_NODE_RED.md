# Solução para Problemas com Node-RED

## Problema: Módulos Faltando

Se você ver erros como "Cannot find module 'body-parser'", tente:

### Opção 1: Reinstalar Dependências

```powershell
cd "C:\Users\pedro.nascimento\AppData\Local\nvm\v20.19.3\node_modules\node-red"
npm install
```

### Opção 2: Reinstalar Node-RED Completamente

```powershell
npm uninstall -g node-red
npm install -g node-red
```

### Opção 3: Instalação Local (Recomendado se der problemas)

Crie uma pasta para o projeto Node-RED:

```powershell
mkdir node-red-project
cd node-red-project
npm init -y
npm install node-red
```

Depois inicie com:
```powershell
npx node-red
```

## Iniciar Node-RED

Após corrigir, inicie com:

```powershell
node-red
```

OU use o arquivo `iniciar-node-red.bat` que foi criado.

## Verificar se Está Funcionando

1. Abra http://localhost:1880
2. Você deve ver a interface do Node-RED
3. Se aparecer, está funcionando!

## Próximo Passo

Depois que o Node-RED estiver rodando:
1. Importe o flow de `node-red-flow-simples.json`
2. Execute `python test-node-red.py` para testar
3. Execute `python main.py` para enviar dados reais

