from cliente_modbus import ClienteMODBUS


def main():
    menu = ClienteMODBUS(server_ip=" localhost", porta=5020, scan_time=1)
    menu.executar()

if __name__ == '__main__':
    main()