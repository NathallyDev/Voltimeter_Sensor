#
# Realizando plotagem de gráfico e salvando em arquivo PDF
# Data: 07/03/2024
#
# Dev: Náthally Lima Arruda 
# e-mail: nathallylym@gmail.com
#
#

import serial
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time

def auto_select_serial_port():
    # Lista todas as portas seriais disponíveis
    ports = serial.tools.list_ports.comports()

    print("Portas seriais disponíveis:")
    for port, desc, hwid in sorted(ports):
        print(f"{port}: {desc} [{hwid}]")

    # Espera 5 segundos para o usuário visualizar a lista de portas
    time.sleep(5)

    # Seleciona automaticamente a primeira porta serial disponível
    if ports:
        selected_port = ports[0].device
        print(f"Porta serial selecionada automaticamente: {selected_port}")
        return selected_port
    else:
        print("Nenhuma porta serial disponível.")
        return None

def read_and_plot_data(modelo, tempo_total_segundos):
    # Inicializa listas para armazenar dados
    tempo_total = []
    tensao_total = []

    # Define o intervalo de leitura em segundos (30 segundos)
    intervalo_leitura = 30

    try:
        # Configuração da porta serial
        ser = serial.Serial('COMx', 9600, timeout=1)  # Substitua 'COMx' pela porta serial correta

        # Tempo inicial
        start_time = time.time()

        while time.time() - start_time < tempo_total_segundos:
            # Leitura da linha serial
            data = ser.readline().decode('utf-8').strip()

            # Dividindo os dados em tempo e tensão
            tempo_atual, tensao_atual = map(int, data.split(','))

            # Adicionando dados às listas
            tempo_total.append(tempo_atual)
            tensao_total.append(tensao_atual)

            # Aguarda o intervalo de leitura
            time.sleep(intervalo_leitura)

    except KeyboardInterrupt:
        pass

    finally:
        # Fechar a porta serial
        ser.close()

        # Plotar o gráfico
        plot_graph(tempo_total, tensao_total, f'Gráfico - Tensão ao Longo do Tempo ({modelo})')

if __name__ == "__main__":
    modelo = input("Digite o modelo (PS-835A, C & E ou PS-835B, D, F & G): ")

    if modelo == "PS-835A, C & E" or modelo == "PS-835B, D, F & G":
        tempo_total_segundos = 45 * 60 if modelo == "PS-835A, C & E" else 90 * 60
        read_and_plot_data(modelo, tempo_total_segundos)
    else:
        print("Modelo inválido. Escolha entre PS-835A, C & E ou PS-835B, D, F & G.")

# Plota o Gráfico
def plot_graph(tempo, tensao, title):
    plt.plot(tempo, tensao)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Tensão')
    plt.title(title)
    plt.show()

def generate_pdf(nome, fabricante, p_n, s_n, modelo, titulo, tempo, tensao, observacao):
    # Gera o PDF com as informações fornecidas
    pdf_filename = f"Relatorio_{time.strftime('%Y%m%d_%H%M%S')}.pdf"

    # Configuração do PDF
    pdf = canvas.Canvas(pdf_filename, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    # Adiciona informações do cabeçalho
    pdf.drawString(72, 750, f"Nome: {nome}")
    pdf.drawString(72, 735, f"Fabricante: {fabricante}")
    pdf.drawString(72, 720, f"P/N: {p_n}")
    pdf.drawString(72, 705, f"S/N: {s_n}")
    pdf.drawString(72, 690, f"Modelo: {modelo}")

    # Adiciona o título do gráfico
    pdf.drawString(72, 660, f"Gráfico - {titulo}")

    # Adiciona observações
    pdf.drawString(72, 630, "Observações:")
    pdf.drawString(72, 615, observacao)

    # Salva o gráfico como uma imagem temporária (pode ajustar o formato conforme necessário)
    plt.plot(tempo, tensao)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Tensão')
    plt.title(titulo)
    plt.savefig("temp_plot.png", format="png")

    # Adiciona a imagem ao PDF
    pdf.drawInlineImage("temp_plot.png", 72, 400, width=400, height=300)

    # Fecha o PDF
    pdf.save()

if __name__ == "__main__":
    # Selecione a porta serial automaticamente ou permita que o usuário escolha
    com_port = auto_select_serial_port() or input("Digite o nome da porta serial (ex. COMx): ")

    # Informações do cabeçalho
    nome = input("Digite o nome do equipamento: ")
    fabricante = input("Digite o fabricante: ")
    p_n = input("Digite o P/N: ")
    s_n = input("Digite o S/N: ")

    # Leitura e plotagem dos dados
    modelo = input("Digite o modelo (PS-835A, C & E ou PS-835B, D, F & G): ")
    tempo_total_segundos = 45 * 60 if modelo == "PS-835A, C & E" else 90 * 60
    tempo, tensao = read_and_plot_data(modelo, tempo_total_segundos, com_port)

    # Título do gráfico
    titulo = f"Tensão ao Longo do Tempo ({modelo})"

    # Observações
    observacao = input("Observações (máximo 1000 palavras): ")

    # Plotar o gráfico
    plot_graph(tempo, tensao, titulo)

    # Gera o PDF
    generate_pdf(nome, fabricante, p_n, s_n, modelo, titulo, tempo, tensao, observacao)

    # Limpa a figura para evitar plotagem adicional no script
    plt.close()
