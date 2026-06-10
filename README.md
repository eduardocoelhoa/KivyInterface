# Cliente Modbus TCP com Interface KivyMD

Aplicacao grafica em Python para leitura e escrita de dados em um servidor Modbus TCP.
A interface foi desenvolvida com KivyMD e utiliza uma classe separada para concentrar a logica de comunicacao Modbus.

## Funcionalidades

- Conexao com servidor Modbus TCP por IP e porta.
- Leitura e escrita de coils.
- Leitura e escrita de Holding Registers.
- Leitura e escrita de valores float.
- Leitura e escrita de bits individuais de um registrador.
- Escrita de multiplos bits de um registrador.
- Leitura unica ou recorrente usando `Clock` do Kivy.
- Indicacao visual do tipo de dado selecionado.
- Area de resultado e log das operacoes.

## Estrutura do projeto

```text
.
├── Cliente/
│   ├── cliente_modbus.py
│   └── main.py
├── Interface/
│   ├── Interface.py
│   └── Interface.kv
├── Servidor/
│   ├── main.py
│   └── servidor_modbus.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Responsabilidades

`Cliente/cliente_modbus.py`

Contem a classe `ClienteMODBUS`, responsavel por:

- abrir e fechar a conexao Modbus TCP;
- ler e escrever coils;
- ler e escrever Holding Registers;
- converter e escrever floats;
- ler e escrever bits de registradores.

`Interface/Interface.py` e `Interface/Interface.kv`

Contem a interface grafica. A tela apenas coleta dados do usuario e chama os metodos da classe `ClienteMODBUS`.

`Servidor/servidor_modbus.py`

Contem um servidor Modbus TCP simples para testes locais.

## Instalação

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Como executar

Para iniciar o servidor de teste:

```powershell
python Servidor/main.py
```

Em outro terminal, com o ambiente virtual ativado, execute a interface:

```powershell
python Interface/Interface.py
```

## Como usar a interface

1. Informe o IP do servidor, por exemplo `127.0.0.1` ou `localhost`.
2. Informe a porta, por exemplo `502`.
3. Clique em `Conectar`.
4. Selecione o tipo de dado: `Coil`, `Holding`, `Float`, `Bit` ou `Bits`.
5. Informe o endereco Modbus.
6. Para escrita, informe o valor no campo correspondente.
7. Clique em `Ler` ou `Escrever`.

Para leitura recorrente, marque a checkbox `Leitura recorrente` e informe o intervalo em segundos.

## Formato dos valores

- `Coil`: use `1`, `0`, `true`, `false`, `ligado` ou `desligado`.
- `Holding`: use um numero inteiro.
- `Float`: use um numero decimal, por exemplo `3.14`.
- `Bit`: use o campo de bit para informar a posicao de `0` a `15`.
- `Bits`: use valores separados por virgula, por exemplo `1,0,1,1`.

No modo `Bits`, o campo de bit indica a posicao inicial da escrita.

## Observacoes

O projeto utiliza `Kivy==2.3.1`, `kivymd==1.2.0` e `pymodbus==3.13.0`, conforme definido em `requirements.txt`.

O aviso de que o KivyMD 1.2.0 esta deprecated nao impede a execucao da aplicacao.
