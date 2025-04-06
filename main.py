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
y_range_index = 1          # Amplitude scale starting index

# Definir funções

""""
def read_samples()
    self.samples = tft.read_adc(240, x_range[x_range_index] * x_div)
        
    if sys.implementation.name == "micropython":
        convert_sample = lambda sample: 0.012049 * sample - 24.059 # IoT 0003.03
    else:
        convert_sample = lambda sample: 0.0129 * sample - 26.62 # Simulator
        
    self.amplitudes = [convert_sample(sample) for sample in self.samples]

def read_and_display_time()
    reset_display
    x, y = [], []

    read_samples

    # Plot sampled values in the current X and Y scale
    y_div_factor = y_range[y_range_index] * y_div / (height - 16)
    x = list(range(len(amplitudes)))
    y = [
        round(max(0, min((height - 16) / 2 + value / y_div_factor, height - 16)))
        for value in amplitudes
    ]
    tft.display_nline(tft.YELLOW, x, y) # Display the plot

"""
def reset_display():
    tft.display_set(tft.BLACK, 0, 0, width, height)         # Erase display
    tft.set_wifi_icon(width - 16, 0)                        # Set wifi icon
    # por tambem as escalas
    # agora temos 2 casos, ou é tempo ou é frequencia"



#def send_email()
    
#def write_to_display()
    
#def x_scale()
#    global x_range_index
#    x_range_index = (x_range_index + 1) % len(x_range)
#    read_and_display()
    
#def y_scale()
    
#def freq_display()
    


# Programa principal (main)

# Passo 1: Inicializar o display apagando-o:
#read_and_display_time()      
reset_display()

# Passo 2: Desenhar a grelha, as escalas e o icon WiFi;
# Passo 3: Realizar uma leitura de valores do ADC, convertê-los para tensões e representar a forma de onda sobre a grelha;
# Passo 4: Aguardar que o utilizador prima um botão:

while tft.working():
    but=tft.readButton()
    if but!=tft.NOTHING:
        print("Button pressed:", but)
        if but == 11:                  # Fast click button 1
            #read_and_display_time()
            reset_display()
        if but == 12:                  # Long click button 1
            send_email()
        if but == 13:                  # Double click button 1
            write_to_display()
        if but == 21:                  # Fast click button 2
            x_scale()
        if but == 22:                  # Long click button 2
            y_scale()
        if but == 23:                  # Double click button 2
            freq_display()
        else: print("Invalid button.")