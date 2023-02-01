#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Modulos a serem utilizados
import pyvisa
import time
import string
import struct
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

rm = pyvisa.ResourceManager()
#verificando o gerenciamento  de recursos
endereco = (rm.list_resources()) 
print (endereco[0])

#Nessa etapa estabelecemos a conexao com osciloscopio
my_instrument = rm.open_resource(endereco[0])
print('comunicação estabelecida:')
print(my_instrument.query('*IDN?'))
print ('')

print ('-------------------------------------------------------------')

#COMANDOS PARA O OSCILOSCÓPIO:
#comandos de canal:
my_instrument.write(':ACQ:TYPE NORM')
my_instrument.write(':ACQ:MODE RTIM')
#Ativando a saida gen out
my_instrument.write(':WGEN:FUNC SIN')
my_instrument.write(':WGEN:OUTP 1')
my_instrument.write(':WGEN:FUNC?')
funcao = my_instrument.read()


#comando para a tensão pico a pico de saída do gerador:
pic_pic = input ('Tensão Pico a Pico do sinal senoidal: ')
pic_pic = float (pic_pic)
my_instrument.write(f':WGEN:VOLT {pic_pic}')
my_instrument.write(':WGEN:VOLT?')
pico_a_pico = my_instrument.read()
pico_a_pico = float (pico_a_pico)
print (f'Tensão de pico a pico do gerador: {pico_a_pico}V')
#Apartir de agora estamos gerando um sinal senoidal, e checando como ele se comporta de pico a pico, apenas observando as diferencas de um a outro

#comando para verificar a tensão de pico positiva de saida do gerador:
my_instrument.write(':WGEN:VOLT:HIGH?')
pico = my_instrument.read()
pico = float (pico)
print (f'Pico alto do gerador:{pico}')

#comando para verificar a tensão de pico negativo de saída do gerador:
my_instrument.write(':WGEN:VOLT:LOW?')
pico_negativo = my_instrument.read()
pico_negativo = float (pico_negativo)
print (f'Pico negativo do gerador:{pico_negativo}')

#comando para o offSet:
my_instrument.write(':WGEN:VOLT:OFFS 0.0')
#comando para verificar o offSet:
my_instrument.write(':WGEN:VOLT:OFFS?')
offset = my_instrument.read()
offset = float (offset)
print (f'OffSet do gerador:{offset}')
# Com isto realizamos o teste se a conexao com osciloscopio, e geracao de ondas esta funcionando corretamente
#Limpando a tela do osciloscopio
my_instrument.write(':CHAN4:DISP 0')
my_instrument.write(':CHAN3:DISP 0')
my_instrument.write(':CHAN1:DISP 0')
my_instrument.write(':CHAN2:DISP 0')

#atribuindo o valor para o Resistor de referência em série com a "caixa preta"
Ref = input ('Resistor de Referência em série com o dispositivo: ')
Ref = float (Ref)
print (f'O Resistor de Referência é: {ref} Ohm')

print('-------------------------------------------------------------------------------------------------------------')

#criando as listas de valores para os parâmetros buscados
list_real = []
list_imag = []
list_freq = []

#iniciando a varredura
#atribuindo valor para a frequencia inicial:
expoente_inic = input ('Expoente inicial para a frequência de base 10: ')
valor_exp = float (expoente_inic)
freq_in = 10**valor_exp

#Realizando os calculos necessarios

print (f'Frequencia inicial: {freq_in}Hz')
while valor_exp <= 5:
    valor_exp = valor_exp + 0.1
    freq = 10**(valor_exp - 0.1)
    fqc = freq
    my_instrument.write(f':WGEN:FREQ {fqc}')
    my_instrument.write(':WGEN:FREQ?')
    frequenciag = my_instrument.read()
    frequenciag = float (frequenciag)

    #Medindo os valores para o canal 1
    my_instrument.write(':MEAS:SOUR CHAN1')
    my_instrument.write(':MEAS:FREQ')
    time.sleep(1)
    my_instrument.write(':MEAS:FREQ?')
    freq1 = my_instrument.read()
    freq1 = float (freq1)
    print (f'Frequência na saída do gerador:{frequenciag}Hz e freq no canal1:{freq1}Hz')
    
    #Amplitude Vpp medida no canal 1
    my_instrument.write(':MEAS:VAMP CHAN1')
    my_instrument.write(':MEAS:VAMP?')
    vpp1 = my_instrument.read()
    vpp1 = float (vpp1)
    #Desligando a visualização do canal 2
    my_instrument.write('CHAN2:DISP 0')
    #Medindo os valores para o canal 2:
    my_instrument.write(':MEAS:SOUR CHAN2')
    
    #Amplitude Vpp no canal 2
    my_instrument.write(':MEAS:VAMP CHAN2')
    my_instrument.write(':MEAS:VAMP?')
    vpp2 = my_instrument.read()
    vpp2 = float (vpp2)
    time.sleep(1)
    my_instrument.write(':AUT')
    time.sleep(1)
    
    #Medindo a defasagem entre os sinais do canal 1 e canal 2 (em grau):
    my_instrument.write(':MEAS:PHAS CHAN1')
    my_instrument.write(':MEAS:PHAS?')
    time.sleep(1)
    defasagem = my_instrument.read()
    ang_def = float(defasagem) 
    #transformando em radianos:
    radiano = ang_def / 180.0 * math.pi
    #fazendo os calculos do cosseno e do  seno:
    coseno = math.cos(-radiano)
    seno = math.sin(radiano)
    rref = Ref 
  
    zreal = ((rref * (vpp2/vpp1) * coseno) - rref) 
    zimag = ((rref*(vpp2/vpp1)) * seno)
    
    print (f'Amplt Res.Ref:{vpp1}V, Amplt do CCTO:{vpp2}V, Ang.Def.:{ang_def}°')
    
    
    print (f'Re[Z*]= {zreal} Ohm, Imag[Z*]={zimag} Ohm,para a frequencia nominal:{frequenciaig}Hz)
    list_real.append(zreal)
    list_imag.append(zimag)
    list_freq.append(frequenciag)
    print ('')
    print ('---------------------------------------------------------------------------------------------------------')
    time.sleep(3)

#Plotando gráfico Re[Z*] e Imag[Z*] x Frequência:

plt.plot(list_freq, list_real,'b')
plt.plot(list_freq, list_imag, 'r')
plt.xscale("log")
plt.ylabel('Re[Z*] e Imag[Z*] ohm')
plt.xlabel('Frequencia Hz')
plt.axis ([10**1.2, max(list_freq), -200, 2000])
plt.show()

print ('Pontos azuis: Re[Z*] medido')
print ('Pontos Amarelos: Imag[Z*] medido')
print ('Azul:Re[Z*] Curva esperada')
print ('Amarelo:Imag[Z*] Curva esperada')

