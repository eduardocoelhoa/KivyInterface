from pathlib import Path
import sys

from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp

sys.path.insert(0, ".")
from Cliente.cliente_modbus import ClienteMODBUS


class Interface(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cliente = None
        self.tipo_dado = "holding"
        self.evento_leitura = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        kv_path = Path(__file__).with_name("Interface.kv")
        return Builder.load_file(str(kv_path))

    def on_start(self):
        self.atualizar_indicador_tipo()

    def conectar(self):
        try:
            ip = self.root.ids.ip_field.text.strip()
            porta = int(self.root.ids.port_field.text)

            self.cliente = ClienteMODBUS(server_ip=ip, porta=porta)
            conectado = self.cliente.conectar()

            if not conectado:
                self.cliente = None
                raise RuntimeError("Nao foi possivel conectar ao servidor Modbus")

            self.root.ids.status_label.text = f"Status: conectado em {ip}:{porta}"
            self.adicionar_log("Conexao realizada")
        except Exception as erro:
            self.exibir_erro(erro)

    def desconectar(self):
        self.parar_leitura_recorrente()

        if self.cliente is not None:
            self.cliente.desconectar()
            self.cliente = None

        self.root.ids.recurrent_checkbox.active = False
        self.root.ids.status_label.text = "Status: desconectado"
        self.adicionar_log("Conexao encerrada")

    def selecionar_tipo(self, tipo_dado):
        self.tipo_dado = tipo_dado
        self.atualizar_indicador_tipo()
        self.adicionar_log(f"Tipo selecionado: {self.obter_nome_tipo(tipo_dado)}")

    def atualizar_indicador_tipo(self):
        cor_selecionado = [0.13, 0.45, 0.85, 1]
        cor_nao_selecionado = [0.88, 0.88, 0.88, 1]
        texto_selecionado = [1, 1, 1, 1]
        texto_nao_selecionado = [0.12, 0.12, 0.12, 1]

        botoes_tipo = {
            "coil": self.root.ids.type_coil_button,
            "holding": self.root.ids.type_holding_button,
            "float": self.root.ids.type_float_button,
            "bit": self.root.ids.type_bit_button,
            "bits": self.root.ids.type_bits_button,
        }

        for tipo, botao in botoes_tipo.items():
            selecionado = tipo == self.tipo_dado
            botao.md_bg_color = cor_selecionado if selecionado else cor_nao_selecionado
            botao.theme_text_color = "Custom"
            botao.text_color = texto_selecionado if selecionado else texto_nao_selecionado

        nome_tipo = self.obter_nome_tipo(self.tipo_dado)
        self.root.ids.selected_type_label.text = f"Selecionado: {nome_tipo}"

    def obter_nome_tipo(self, tipo_dado):
        nomes = {
            "coil": "Coil",
            "holding": "Holding Register",
            "float": "Float",
            "bit": "Bit individual",
            "bits": "Multiplos bits",
        }
        return nomes.get(tipo_dado, tipo_dado)

    def ler(self):
        try:
            self.verificar_cliente_conectado()
            endereco = self.obter_endereco()
            resultado = self.ler_valor(endereco)
            self.root.ids.result_label.text = str(resultado)
            self.adicionar_log(f"Leitura {self.tipo_dado} no endereco {endereco}: {resultado}")
        except Exception as erro:
            self.exibir_erro(erro)

    def escrever(self):
        try:
            self.verificar_cliente_conectado()
            endereco = self.obter_endereco()
            valor = self.root.ids.value_field.text.strip()

            if self.tipo_dado == "coil":
                self.cliente.escrever_coil(endereco, self.converter_texto_para_bool(valor))
            elif self.tipo_dado == "holding":
                self.cliente.escrever_holding_register(endereco, int(valor))
            elif self.tipo_dado == "float":
                self.cliente.escrever_float(endereco, float(valor))
            elif self.tipo_dado == "bit":
                self.cliente.escrever_bit(endereco, self.obter_bit(), self.converter_texto_para_bool(valor))
            elif self.tipo_dado == "bits":
                self.cliente.escrever_bits(endereco, self.converter_texto_para_bits(valor), self.obter_bit())
            else:
                raise ValueError("Tipo de dado invalido")

            self.root.ids.result_label.text = "Escrita realizada com sucesso"
            self.adicionar_log(f"Escrita {self.tipo_dado} no endereco {endereco}: {valor}")
        except Exception as erro:
            self.exibir_erro(erro)

    def ler_valor(self, endereco):
        if self.tipo_dado == "coil":
            return self.cliente.ler_coil(endereco)
        if self.tipo_dado == "holding":
            return self.cliente.ler_holding_register(endereco)
        if self.tipo_dado == "float":
            return self.cliente.ler_float(endereco)
        if self.tipo_dado == "bit":
            return self.cliente.ler_bit(endereco, self.obter_bit())
        if self.tipo_dado == "bits":
            return self.cliente.ler_bits(endereco)
        raise ValueError("Tipo de dado invalido")

    def alternar_leitura_recorrente(self, ativo):
        if ativo:
            self.iniciar_leitura_recorrente()
        else:
            self.parar_leitura_recorrente()

    def iniciar_leitura_recorrente(self):
        self.parar_leitura_recorrente()

        try:
            self.verificar_cliente_conectado()
            intervalo = float(self.root.ids.interval_field.text)

            if intervalo <= 0:
                raise ValueError("Intervalo deve ser maior que zero")

            self.evento_leitura = Clock.schedule_interval(self.ler, intervalo)
            self.adicionar_log(f"Leitura recorrente ativada a cada {intervalo}s")
        except Exception as erro:
            self.root.ids.recurrent_checkbox.active = False
            self.exibir_erro(erro)

    def parar_leitura_recorrente(self):
        if self.evento_leitura is not None:
            self.evento_leitura.cancel()
            self.evento_leitura = None
            self.adicionar_log("Leitura recorrente desativada")

    def verificar_cliente_conectado(self):
        if self.cliente is None:
            raise RuntimeError("Conecte ao servidor Modbus antes de ler ou escrever")

    def obter_endereco(self):
        texto = self.root.ids.address_field.text.strip()
        if texto == "":
            raise ValueError("Informe o endereco Modbus")
        return int(texto)

    def obter_bit(self):
        texto = self.root.ids.bit_field.text.strip()
        if texto == "":
            raise ValueError("Informe a posicao do bit")

        bit = int(texto)
        if bit < 0 or bit > 15:
            raise ValueError("A posicao do bit deve estar entre 0 e 15")
        return bit

    def converter_texto_para_bool(self, texto):
        valor = texto.strip().lower()
        if valor in ("1", "true", "on", "ligado"):
            return True
        if valor in ("0", "false", "off", "desligado"):
            return False
        raise ValueError("Use 1/0 ou true/false para valores booleanos")

    def converter_texto_para_bits(self, texto):
        partes = [parte.strip() for parte in texto.split(",") if parte.strip()]

        if not partes:
            raise ValueError("Informe bits separados por virgula. Exemplo: 1,0,1,1")
        if len(partes) > 16:
            raise ValueError("Informe no maximo 16 bits")

        bits = [int(parte) for parte in partes]
        if any(bit not in (0, 1) for bit in bits):
            raise ValueError("Cada bit deve ser 0 ou 1")
        return [bool(bit) for bit in bits]

    def adicionar_log(self, mensagem):
        log_atual = self.root.ids.log_label.text
        self.root.ids.log_label.text = f"{log_atual}\n{mensagem}".strip()

    def exibir_erro(self, erro):
        mensagem = f"Erro: {erro}"
        self.root.ids.result_label.text = mensagem
        self.adicionar_log(mensagem)


if __name__ == "__main__":
    Interface().run()
