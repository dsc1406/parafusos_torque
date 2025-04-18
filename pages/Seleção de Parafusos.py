import streamlit as st
import pandas as pd
import os

def soma_lista_segura (lista):
    valores_validos = [x for x in lista if x is not None and not pd.isna(x)]
    return sum(valores_validos)

def main():

    # Carregando planilhas e configurção dos itens ------------------------------------------------------------------------------
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    diretorio_pai = os.path.dirname(diretorio_atual)
    caminho_destino = os.path.join(diretorio_pai, 'Arquivos_extras')
    destino_arruelas = os.path.join(caminho_destino, 'informacoes_arruelas.csv')
    destino_parafusos = os.path.join(caminho_destino, 'informacoes_parafusos.csv')

    df_arruelas = pd.read_csv(destino_arruelas, index_col=0)
    df_parafusos = pd.read_csv(destino_parafusos, index_col=0)

    st.set_page_config(page_title="BoltMate - Seleção de Parafuso", layout="wide", page_icon='🔧')
    
    col = st.columns([0.1,0.8,0.1])
    
    # Layout ------------------------------------------------------------------------------
    with col[1]:
        st.title('🔧BoltMate - Seleção de Parafusos🔧')  

        with st.container(border=True):
            col1, col2 = st.columns(2)

            # para espessuras -----------------------------------------------------------------
            with col1:
                with st.container(border=True):
                    tamanho_parafuso = st.selectbox('Tamanho Nominal Parafuso', df_parafusos['Tamanho'].unique().tolist(), placeholder='Selecione o Tamanho do Parafuso'),
                    quantidade_chapas = st.number_input('Quantidade de Chapas', min_value=1, step=1, placeholder='Numero de Chapas a ser Fixadas')

                with st.container(border=True):
                    
                    if quantidade_chapas != None:
                            esp = []                            
                            for i in range(quantidade_chapas):
                                valor = st.number_input(f"Espessura da Chapa {i+1}", min_value=0.0, value=None, placeholder='Espessura em mm...', key=f"var_{i}")
                                esp.append(valor)

            with col2:                
                with st.container(border=True):
                    tipo_arruela = st.radio('Seleção de Arruelas', ['Padrão', 'Especial', 'Sem Arruela'], horizontal=True)

                    if tipo_arruela == 'Padrão':
                        arruelas = st.multiselect('Selecione as Arruelas que serão usadas:', options=['Lisa - DIN 125-1', 'Pressão - DIN 127'], default=['Lisa - DIN 125-1', 'Pressão - DIN 127'])
                    elif tipo_arruela == 'Especial':
                        arruelas = st.number_input('Digite a espessura da arruela (em mm)', min_value=0, value=0, placeholder='Espessura em mm...')

                # Ancoragem ----------------------------------------------------------
                with st.container(border=True):
                    tipo_ancoragem = st.radio('Tipo de Ancoragem', ['Chapa (Furo Passante)', 'Porca - DIN 934', 'Peça'], horizontal=True)

                    if tipo_ancoragem == 'Chapa (Furo Passante)':
                        ancoragem = st.number_input('Digite a espessura da chapa (em mm)', min_value=0.0, value=0.0, placeholder='Espessura em mm...')

                    elif tipo_ancoragem == 'Porca - DIN 934':
                        tipo_arruela_porca = st.radio('Seleção de Arruelas', ['Padrão', 'Especial', 'Sem Arruela'], horizontal=True, key='arruela_porca')

                        if tipo_arruela_porca == 'Padrão':
                            ancoragem = st.multiselect('Selecione as Arruelas que serão usadas:', ['Lisa - DIN 125-1', 'Pressão - DIN 127'], default=['Lisa - DIN 125-1', 'Pressão - DIN 127'], key='tipo_arruela_porca')

                        elif tipo_arruela_porca == 'Especial':
                            ancoragem = st.number_input('Digite a espessura da arruela', min_value=0, value=0, placeholder='Espessura em mm...', key='arruela_especial_porca')
                        
                        else:
                            ancoragem = 0

                    elif tipo_ancoragem == 'Peça':
                        ancoragem = st.number_input('Digite a profundidade da rosca (em mm)', min_value=0, value=0, placeholder='Profundidade em mm...')

        # Cálculo de espessura total ---------------------------------------------------------------------------------------------------------------------
        soma_espessura = soma_lista_segura(esp)

        if tipo_arruela == 'Sem Arruela':
            arruelas = 0

        if isinstance(arruelas, list):
            soma_arruela = df_arruelas.loc[df_arruelas['Tamanho Parafuso'] == str(tamanho_parafuso[0]), arruelas].sum(axis=1).values[0]

        elif isinstance(arruelas, int):
            soma_arruela = arruelas
        


        espessura_total = soma_espessura + soma_arruela

        # Cálculo Ancoragem -----------------------------------------------------------------------------------------------------------------------------------
        esp_porca = df_arruelas.loc[df_arruelas['Tamanho Parafuso'] == str(tamanho_parafuso[0]), 'Porca - DIN 934'].reset_index(drop=True)[0]

        if isinstance(ancoragem, list):
            espessura_total = espessura_total + df_arruelas.loc[df_arruelas['Tamanho Parafuso'] == str(tamanho_parafuso[0]), ancoragem].sum(axis=1).values[0]
            soma_ancoragem = esp_porca

        elif tipo_ancoragem == 'Porca - DIN 934' and tipo_arruela_porca != 'Padrão':
            espessura_total = espessura_total + ancoragem
            soma_ancoragem = esp_porca
        
        else:
            soma_ancoragem = ancoragem
        
        # Tabela ---------------------------------------------------------------
        df_show = df_parafusos.loc[df_parafusos['Tamanho'] == str(tamanho_parafuso[0]),:]
        df_show['Rosca Engajada'] = df_show['Comprimento'] - espessura_total

        if tipo_ancoragem == 'Porca':
            df_show['Rosca Engajada'] = df_show['Rosca Engajada'].apply(lambda x: x if x < esp_porca else esp_porca)
        else:
            df_show['Rosca Engajada'] = df_show['Rosca Engajada'].apply(lambda x: x if x < soma_ancoragem else soma_ancoragem)

        idx = df_show[df_show['Rosca Engajada'] > 0].index.min()
        df_show = df_show.loc[idx:idx+5,:]
        df_show = df_show.set_index('Tamanho')

        if not df_show.empty:
            st.table(df_show)
        trocar_pagina = st.button('Voltar - Cálculadora de Torque')   

    if trocar_pagina:
        st.switch_page('Home.py')

if __name__ == "__main__":
    main()