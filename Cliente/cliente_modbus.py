from pymodbus.client import ModbusTcpClient


class ClienteMODBUS:
    """
    Cliente responsavel pela comunicacao Modbus TCP.
    A interface grafica deve apenas chamar os metodos desta classe.
    """

    def __init__(self, server_ip=None, porta=None, host=None, port=None, scan_time=1):
        resolved_host = host if host is not None else server_ip
        resolved_port = port if port is not None else porta

        if resolved_host is None or resolved_port is None:
            raise ValueError("server_ip/porta or host/port must be provided")

        self._client = ModbusTcpClient(host=resolved_host, port=resolved_port)
        self._scan_time = scan_time

    def conectar(self):
        """
        Abre a conexao com o servidor Modbus.
        """
        return self._client.connect()

    def desconectar(self):
        """
        Fecha a conexao com o servidor Modbus.
        """
        self._client.close()

    def _validar_resposta(self, resp):
        if resp is None:
            raise RuntimeError("Servidor Modbus nao respondeu")
        if hasattr(resp, "isError") and resp.isError():
            raise RuntimeError(f"Erro Modbus: {resp}")
        return resp

    def _validar_posicao_bit(self, posicao):
        if posicao < 0 or posicao > 15:
            raise ValueError("A posicao do bit deve estar entre 0 e 15")

    def ler_holding_register(self, endereco, quantidade=1, device_id=1):
        """
        Le um ou mais Holding Registers.
        """
        resp = self._client.read_holding_registers(
            address=endereco,
            count=quantidade,
            device_id=device_id,
        )
        self._validar_resposta(resp)

        if quantidade == 1:
            return resp.registers[0]
        return resp.registers

    def escrever_holding_register(self, endereco, valor, device_id=1):
        """
        Escreve um valor inteiro em um Holding Register.
        """
        resp = self._client.write_register(
            address=endereco,
            value=int(valor),
            device_id=device_id,
        )
        return self._validar_resposta(resp)

    def ler_float(self, endereco, device_id=1):
        """
        Le um float armazenado em dois Holding Registers consecutivos.
        """
        resp = self._client.read_holding_registers(
            address=endereco,
            count=2,
            device_id=device_id,
        )
        self._validar_resposta(resp)
        return self._client.convert_from_registers(
            resp.registers,
            self._client.DATATYPE.FLOAT32,
        )

    def escreve_float(self, endereco, valor, device_id=1):
        """
        Escreve um float em dois Holding Registers consecutivos.
        """
        registros = self._client.convert_to_registers(
            float(valor),
            self._client.DATATYPE.FLOAT32,
        )
        resp = self._client.write_registers(
            address=endereco,
            values=registros,
            device_id=device_id,
        )
        return self._validar_resposta(resp)

    def escrever_float(self, endereco, valor, device_id=1):
        """
        Alias para escreve_float.
        """
        return self.escreve_float(endereco, valor, device_id=device_id)

    def ler_coil(self, endereco, quantidade=1, device_id=1):
        """
        Le uma ou mais coils.
        """
        resp = self._client.read_coils(
            address=endereco,
            count=quantidade,
            device_id=device_id,
        )
        self._validar_resposta(resp)

        if quantidade == 1:
            return resp.bits[0]
        return resp.bits[:quantidade]

    def escrever_coil(self, endereco, valores, device_id=1):
        """
        Escreve uma coil ou uma lista de coils.
        """
        if isinstance(valores, bool):
            resp = self._client.write_coil(
                address=endereco,
                value=valores,
                device_id=device_id,
            )
        else:
            resp = self._client.write_coils(
                address=endereco,
                values=valores,
                device_id=device_id,
            )
        return self._validar_resposta(resp)

    def ler_bits_do_registrador(self, endereco, device_id=1):
        """
        Le todos os bits de um Holding Register.
        """
        valor = self.ler_holding_register(endereco, quantidade=1, device_id=device_id)
        return [bool(valor & (1 << bit)) for bit in range(16)]

    def ler_bits(self, endereco, device_id=1):
        """
        Alias usado pela interface para ler todos os bits de um registrador.
        """
        return self.ler_bits_do_registrador(endereco, device_id=device_id)

    def ler_bit(self, endereco, posicao, device_id=1):
        """
        Le um bit especifico de um Holding Register.
        """
        self._validar_posicao_bit(posicao)
        bits = self.ler_bits_do_registrador(endereco, device_id=device_id)
        return bits[posicao]

    def ler_bits_do_registrador(self, endereco, device_id=1):
        """
        Lê os bits de um Holding Register e retorna uma lista de booleanos
        """
        resp = self._client.read_holding_registers(address=endereco, count=1, device_id=device_id)
        return self._client.convert_from_registers(resp.registers, self._client.DATATYPE.BITS)

    def escrever_bit(self, endereco, posicao, estado, device_id=1):
        """
        Escreve multiplos bits de um Holding Register preservando os demais bits.
        """
        resp = self._client.read_holding_registers(address=endereco, count=1, device_id=device_id)
        bits = self._client.convert_from_registers(resp.registers, self._client.DATATYPE.BITS)

        bits[posicao] = estado

        registros = self._client.convert_to_registers(bits, self._client.DATATYPE.BITS)
        return self._client.write_registers(address=endereco, values=registros, device_id=device_id)
