#!/usr/bin/env python3
import sys
import T_Display
import time
import math
import cmath
#import gc

# Variables
tft = T_Display.TFT()      # TFT display interface
width = 240                # Max width (px)
height = 135               # Max height (px)
x_div = 10                 # Number of horizontal divisions
x_range = [5, 10, 20, 50]  # Time scale (ms)
x_range_freq = [240, 120, 60, 24] # Freq scale (Hz)
x_range_index = 0          # Time scale starting index
y_div = 6                  # Number of vertical divisions
y_range = [1, 2, 5, 10]    # Amplitude scale (V)
y_range_index = 0          # Amplitude scale starting index
fator = 1/29.3  # Fator do divisor resistivo

# Definir funções


def read_display(x_range_index, y_range_index):
    pontos_adc = tft.read_adc(width, x_range[x_range_index]*10)
    tensoes_aux = pontos_adc
    Vmax = 0
    Vmin = 0
    Vmed = 0
    Vrms = 0
    x = []
    y = []
    for n in range(width):
        # Converte valor do ADC em Volt
        # V = 0.00044028 * pontos_adc[n] + 0.091455 (Calibração do professor)
        V = 0.0004313133*pontos_adc[n]+0.10264  # Nossa calibração
        V = V - 1                                 # Tensão entrada de referência de 1V
        V = V / fator                             # Entra com o efeito do div. resistivo
        tensoes_aux[n] = V
        pixel = (height - 16)/2 + 16 + ((height - 16)/(6*y_range[y_range_index])) * V
        if pixel > height:  # Quando o valor excede o espaço vertical superior simplesmente fica no limite superior do display
            pixel = height
        if pixel < 16:   # Quando o valor excede o espaço vertical inferior simplesmente fica no limite inferior do display
            pixel = 16

        x.append(n)
        y.append(round(pixel))

        if n == 0:       # Caso seja o primeiro ponto
            Vmax = Vmin = Vmed = Vrms = V
        else:
            Vmed += V
            if V > Vmax:
                Vmax = V
            if V < Vmin:
                Vmin = V

    tft.display_set(tft.BLACK, 0, 0, width, height)  # Apaga display
    tft.display_write_grid(0, 16, width, height-16, 10, 6,
                            tft.GREY1, tft.GREY2)  # Desenha grelha
    tft.set_wifi_icon(width-16, 0)  # Adiciona wifi icon
    # escrever a escala no topo
    tft.display_write_str(tft.Arial16, "%d ms/div" %
                            x_range[x_range_index], 0, 0)
    tft.display_write_str(tft.Arial16, "%d V/div" %
                            y_range[y_range_index], 45+35, 0)
    # imprimir a forma de onda
    tft.display_nline(tft.YELLOW, x, y)

    Vrms = 0
    for i in range(len(tensoes_aux)):
        Vrms += (tensoes_aux[i]*tensoes_aux[i])

    Vrms = math.sqrt(Vrms / len(tensoes_aux))

    Vmed /= 240  # Divide pelo número de amostras

    return Vmax, Vmin, Vmed, Vrms, tensoes_aux

def send_email(max_value, min_value, med_value, rms_value, tensoes_array):
    corpo_mail = "Lista de %d pontos em %.2f segundos.\n Vmax = %.3fV \n Vmin = %.3fV \n Vmed = %.3fV \n Vrms = %.3fV\n" % (width, (x_range[x_range_index]*10)*0.001, max_value, min_value, med_value, rms_value)
    tft.send_mail(((x_range[x_range_index]*10)*0.001)/width, tensoes_array, corpo_mail, "jose.felix.da.fonseca@tecnico.ulisboa.pt,matilde.assis.nunes@tecnico.ulisboa.pt,rodrigo.moura@tecnico.ulisboa.pt")

def y_scale(y_range_index):
    y_range_index -= 1
    if (y_range_index < 0):  # alterar a escala vertical de forma circular
        y_range_index = 3
    return y_range_index

def x_scale(x_range_index):
    x_range_index -= 1
    if (x_range_index < 0):  # alterar a escala vertical de forma circular
        x_range_index = 3
    return x_range_index

def dft(amplitudes):
    N = len(amplitudes)
    mag = [0.0] * N

    for k in range(N // 2 - 1):
        real, imag = 0.0, 0.0
        for n in range(N):
            theta = -2 * math.pi * k * n / N
            real += amplitudes[n] * math.cos(theta)
            imag += amplitudes[n] * math.sin(theta)

        magnitude = math.sqrt(real ** 2 + imag ** 2) / N
        if k != 0:
            magnitude *= 2

        # Duplicate magnitude values for smoother visualization (240 samples)
        mag[2 * k] = magnitude
        mag[2 * k + 1] = magnitude

    return mag

def freq_display(max_value, min_value, med_value, rms_value, tensoes_array):
    """
    Displays the frequency spectrum of the signal on the TFT display.
    """
    spectrum = dft(tensoes_array)
    max_magnitude = max(spectrum) or 1  # Prevent division by zero

    x = []
    y = []

    usable_height = height - 16
    for n in range(width):
        magnitude = spectrum[n]
        # Ajustando a escala para que as maiores magnitudes fiquem no topo
        pixel = 16 + usable_height * (magnitude / max_magnitude)  # Maior magnitude vai para o topo
        pixel = min(max(16, pixel), height)  # Respeitar os limites verticais
        x.append(n)  # Ou x.append(width - 1 - n) para inverter o eixo X
        y.append(round(pixel))

    # Draw display
    tft.display_set(tft.BLACK, 0, 0, width, height)
    tft.display_write_grid(0, 16, width, height - 16, 10, 6, tft.GREY1, tft.GREY2)
    tft.set_wifi_icon(width - 16, 0)
    tft.display_write_str(tft.Arial16, "%d Hz/div" % x_range_freq[x_range_index], 0, 0)
    tft.display_write_str(tft.Arial16, "%d V/div" % y_range[y_range_index], 45+35, 0)
    tft.display_nline(tft.YELLOW, x, y)


def apply_filter(input_signal):
    output_signal = [0.0] * len(input_signal)

    for n in range(len(input_signal)):
        x_n   = input_signal[n]
        x_n_2 = input_signal[n - 2] if n >= 2 else 0.0
        y_n_1 = output_signal[n - 1] if n >= 1 else 0.0
        y_n_2 = output_signal[n - 2] if n >= 2 else 0.0

        y_n = 0.03163 * x_n - 0.03163 * x_n_2 + 1.9292 * y_n_1 - 0.93674 * y_n_2
        output_signal[n] = y_n

    return output_signal

def LPF_Filter(max_value, min_value, med_value, rms_value, tensoes_array):
    # Aplica o filtro
    filtrado = apply_filter(tensoes_array)

    # Variáveis para display
    x = []
    y = []

    for n in range(width):
        V = filtrado[n]
        pixel = (height - 16)/2 + 16 + ((height - 16)/(6*y_range[y_range_index])) * V

        if pixel > height:
            pixel = height
        if pixel < 16:
            pixel = 16

        x.append(n)
        y.append(round(pixel))

    # Redesenha o display com sinal filtrado
    tft.display_set(tft.BLACK, 0, 0, width, height)  # Apaga display
    tft.display_write_grid(0, 16, width, height - 16, 10, 6, tft.GREY1, tft.GREY2)  # Grelha
    tft.set_wifi_icon(width - 16, 0)  # Ícone WiFi
    tft.display_write_str(tft.Arial16, "%d ms/div" % x_range[x_range_index], 0, 0)
    tft.display_write_str(tft.Arial16, "%d V/div" % y_range[y_range_index], 80, 0)

    # Desenha o sinal filtrado
    tft.display_nline(tft.GREEN, x, y)  # Usamos VERDE para distinguir o sinal filtrado


# Programa principal (main)

# Passo 1: Inicializar o display apagando-o:
#read_and_display_time()      
max_value, min_value, med_value, rms_value, tensoes_array = read_display(x_range_index, y_range_index)

# Passo 2: Desenhar a grelha, as escalas e o icon WiFi;
# Passo 3: Realizar uma leitura de valores do ADC, convertê-los para tensões e representar a forma de onda sobre a grelha;
# Passo 4: Aguardar que o utilizador prima um botão:

while tft.working():
    but=tft.readButton()
    if but!=tft.NOTHING:
        print("Button pressed:", but)
        if but == 11:                  # Fast click button 1
            max_value, min_value, med_value, rms_value, tensoes_array = read_display(x_range_index, y_range_index)
        if but == 12:                  # Long click button 1
            send_email(max_value, min_value, med_value, rms_value, tensoes_array)
        if but == 13:                  # Double click button 1
            LPF_Filter(max_value, min_value, med_value, rms_value, tensoes_array)
        if but == 21:                  # Fast click button 2
            y_range_index = y_scale(y_range_index)
            max_value, min_value, med_value, rms_value, tensoes_array = read_display(x_range_index, y_range_index)
        if but == 22:                  # Long click button 2
            x_range_index = x_scale(x_range_index)
            max_value, min_value, med_value, rms_value, tensoes_array = read_display(x_range_index, y_range_index)
        if but == 23:                  # Double click button 2
            freq_display(max_value, min_value, med_value, rms_value, tensoes_array)
        else: print("Invalid button.")