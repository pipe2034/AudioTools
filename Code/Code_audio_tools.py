#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 12:25:57 2020

@author: daniel
"""

import numpy as np
import scipy.io.wavfile as wavf
import os
from pydub import AudioSegment
import sys
import shutil
from tqdm import tqdm
import scipy.io.wavfile as waves
import argparse
from shutil import rmtree

def audio_with_silence(file,T):
       # Calculate target number of samples
    one_sec_segment = AudioSegment.silent(duration=T)  #duration in milliseconds
    
    #read wav file to an audio segment
    song = AudioSegment.from_wav(file)
    
    #Add above two audio segments    
    final_song =  song + one_sec_segment 
    
    return final_song, len(one_sec_segment)
    #Either save modified audio

def retrieve_audio(file,samples_add):     
    song_complete = AudioSegment.from_wav(file)
    final_song= song_complete[0:-samples_add]
    return final_song

def channel_normalization(path_audios, path_save):

    
    #Path temporal para codificar audios
    path_temp = './audios_encoded'
    
    #Crear carpeta para guardar resultados
    if os.path.isdir(path_save)==False:
        os.makedirs(path_save)
        
    #Crear carpeta para guardar resultados
    if os.path.isdir(path_temp)==False:
        os.makedirs(path_temp)
    
    #Lista de archivos a normalizar
    list_audios = os.listdir(path_audios)
    print('channel normalization in process')
    for i in tqdm(range(len(list_audios))):
#        print('Normalizando',iFile)   
        """
        Pasos para normalizar canal
        1. Convertir a mono: -c 1
        2. Reducir la tasa de bits por segundo a 13bps: -e gsm-full-rate
        3. Remuestrear a 8kHz: -r 8000
        4. Comprimir con un factor de 8: -C 8
        5. Aplicar filtro pasabandas de 200Hz a 3.4kHz:sinc 200-3.4k
        """
        os.system('sox '+path_audios+'/'+list_audios[i]+' -c 1 -e gsm-full-rate -r 8000 -C 8 '+path_temp+'/'+list_audios[i]+' sinc 200-3.4k')
        
    """
    El canal de los audios ya estan normalizados, sin embargo, dado que estan codificados a 13 bits 
    es imposible usarlos en Python. Por eso, debemos decodificarlos a 16 bits, sin afectar 
    el proceso de normalizacion de canal
    """ 
    #Lista de archivos a normalizar
    list_audios = os.listdir(path_temp)
    for i in tqdm(range(len(list_audios))):
#        print('Decodificando a 16 bits',iFile)
        os.system('sox '+path_temp+'/'+list_audios[i]+' -b 16 '+path_save+'/'+list_audios[i])
        
    shutil.rmtree(path_temp)

def add_contained(path_audios,path_audios_extend):
    files = os.listdir(path_audios)
    fileDict={}
    for file in files:
        fs, audio = wavf.read(path_audios+'/'+file)
        timeAudio = 1/fs*len(audio)
        if timeAudio <= 3:
            timeAdd = 3-timeAudio
            final_song, fileDict[file] = audio_with_silence(path_audios+'/'+file,timeAdd*1000)
        else:
            final_song = AudioSegment.from_wav(path_audios+'/'+file)
        
        final_song.export(path_audios_extend+'/'+file, format="wav")
            
    return fileDict
            
def removeContent(path_audios,path_Outaudios, fileDict):
    files = os.listdir(path_audios)         
    for file in files:     
        if file in list(fileDict.keys()):
            final_song = retrieve_audio(path_audios+'/'+file, fileDict[file])
        else:
            final_song = AudioSegment.from_wav(path_audios+'/'+file)
        if not(os.path.isdir(path_Outaudios)):
            os.makedirs(path_Outaudios) 
        final_song.export(path_Outaudios+'/'+file, format="wav")


def ChangeMonoChannel(path_audios, path_destino, chanel = 1):
    files = os.listdir(path_audios)
    for file in files:
        fs, sonido = waves.read(path_audios+'/'+file)    
        if len(sonido.shape) > 1:
            sonido = sonido[:,chanel]

        waves.write(path_destino+'/'+file, fs, sonido)


#Funtions integrate with arguments        
def removeNoise(args):
    pathOriginal = args.path[0]
    path_model = '../models/clc.pt'
    path_des = args.path_des[0]
    if os.path.isdir(pathOriginal+'_temp')==False:
        os.makedirs(pathOriginal+'_temp')
    if os.path.isdir(pathOriginal+'_temp1')==False:
        os.makedirs(pathOriginal+'_temp1')            
    fileDict=add_contained(pathOriginal,pathOriginal+'_temp')    
    ChangeMonoChannel(pathOriginal+'_temp',pathOriginal+'_temp')
    print('Remove Noise\n')
    os.system('./removeNoise.sh '+path_model+' '+ pathOriginal+'_temp/ '+  pathOriginal+'_temp1/')
    removeContent(pathOriginal+'_temp1',path_des,fileDict)
    rmtree(pathOriginal+'_temp')
    rmtree(pathOriginal+'_temp1')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Toolkit for pre-processing audio problems')

    subparsers = parser.add_subparsers(help='code with tools for problems with Audio')
    parser_data = subparsers.add_parser('removeNoise', help='using model pretrained')
    parser_data.add_argument('-path', help='path_with_audios', type=str, required=True, nargs='+')
    parser_data.add_argument('-path_des', help='Destination Path', type=str, required=True, nargs='+')
    parser_data.set_defaults(func=removeNoise)
        
    args = parser.parse_args()
    args.func(args)
