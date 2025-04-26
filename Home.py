import streamlit as st
import pandas as pd
import os

def main():  
    st.set_page_config(page_title="BoltMate - Cálculo de Torque", layout="wide", page_icon='🔧')

    dados = {
    "Material": ["ASTM A36", "Aço Inoxidável 304"],
    "Resistência ao Cisalhamento (MPa)": [240, 345]
    }
    df_cisalhamento = pd.DataFrame(dados)

    path = os.path.join('Arquivos_extras', 'informacoes_filtradas.csv')
    df = pd.read_csv(path)
    df.sort_values(['Material', 'Torque de Montagem (Nm)'],ascending=True,inplace=True)

    path_torque = os.path.join('Arquivos_extras', 'torque_parafusos.csv')
    df_torque = pd.read_csv(path_torque, index_col='Tamanho')

    materiais_disponiveis = list(df['Material'].unique())
    tamanhos_disponiveis = list(df['Rosca'].unique())

    col = st.columns([0.1,0.8,0.1])

    with col[1]:    
        st.title('🔧BoltMate - Calculadora de Torque em Parafusos🔧') 
        st.caption("Desenvolvido por Diego Carneiro · 2025 - App: BoltMate")
        
        with st.container(border=True):
            
            col = st.columns(2)
            with col[0]:
                
                material = st.selectbox('Material do Parafuso', materiais_disponiveis,
                    index=materiais_disponiveis.index(st.session_state.get("material")) if st.session_state.get("material") in materiais_disponiveis else None,
                    placeholder='Selecione o Material')
                st.session_state["material"] = material

                
                rosca_engajada = st.number_input('Comprimento de Rosca Engajada (mm)', min_value=0.0, step=0.1,
                    value=st.session_state.get("rosca_engajada", 0.0), placeholder='Digite o Comprimento da Rosca')
                st.session_state["rosca_engajada"] = rosca_engajada

                calcular = st.button('Calcular')
                                
            with col[1]:
                
                tamanho_parafuso = st.selectbox('Tamanho Nominal Parafuso', tamanhos_disponiveis,
                    index=tamanhos_disponiveis.index(st.session_state.get("tamanho_parafuso")) if st.session_state.get("tamanho_parafuso") in tamanhos_disponiveis else None,
                    placeholder='Selecione o Tamanho do Parafuso')
                st.session_state["tamanho_parafuso"] = tamanho_parafuso

                if material == 'Aço Carbono (A36)':
                    classes_disponiveis = df_torque.iloc[:,:4].columns
                else:
                    classes_disponiveis = df_torque.iloc[:,4:].columns

                classe_parafuso = st.selectbox('Classe do Parafuso', classes_disponiveis, index=None, placeholder='Escolha a Classe do Parafuso...')

                selecao_parafuso = st.button('Cálculo de Rosca Engajada - Seleção de Parafuso')

        if calcular: 
            if material != None and tamanho_parafuso != None and classe_parafuso != None:     
                df_filtrado = df.loc[(df['Material'] == material) & (df['Rosca'] == tamanho_parafuso),:].reset_index(drop=True)
                rosca_minima = df_filtrado.loc[0, 'Comprimento Roscado(mm)']
                torque_max_paraf = df_torque.loc[tamanho_parafuso,classe_parafuso]

                if rosca_engajada != None:
                    if rosca_engajada > rosca_minima:
                        torque_montagem = round((df_filtrado.loc[0,'Torque de Montagem (Nm)'] * rosca_engajada) / df_filtrado.loc[0,'Comprimento Roscado(mm)'])

                        if torque_montagem < torque_max_paraf:
                            with st.container(border=True):
                                col = st.columns(3)

                                with col[0]:
                                    carga_maxima = round((df_filtrado.loc[0,'Carga Máxima (kg)'] * rosca_engajada) / df_filtrado.loc[0,'Comprimento Roscado(mm)'])
                                    st.metric(label='Carga Máxima', value=str(carga_maxima) + ' kg', border=True)

                                with col[1]:                                
                                    st.metric(label='Torque de Montagem', value=str(torque_montagem) + ' Nm', border=True)

                                with col[2]:
                                    torque_max = round((df_filtrado.loc[0,'Torque Máximo (Nm)'] * rosca_engajada) / df_filtrado.loc[0,'Comprimento Roscado(mm)'])
                                    st.metric(label='Torque Máximo', value=str(torque_max) + ' Nm', border=True)
                        else:
                            st.warning(f'O torque de montagem e maior que o Torque suportado pelo parafuso.')
                            st.info(f'O torque de montagem é {torque_montagem} Nm')
                            st.info(f'O torque de máximo do parafuso é {int(torque_max_paraf)} Nm')
                    else:
                        st.warning(f'O mínimo de rosca engajada para parafusos {tamanho_parafuso} é de {rosca_minima} mm')                        
                else:
                    st.warning('Preencha todos os valores para realizar o cálculo')
            else:
                st.warning('Preencha todos os valores para realizar o cálculo')
        
        if selecao_parafuso:
            st.switch_page('pages/Seleção de Parafusos.py')

        st.divider()
        st.markdown('### 📘Definições')
        st.markdown('''
        - **Material do Parafuso** — Material no qual o parafuso está sendo rosqueado.

        - **Carga Máxima** — Força de tração no parafuso necessária para arrancar (strippagem) as roscas do material base.

        - **Comprimento de Rosca Engajada** — Distância axial ao longo da qual as roscas completamente formadas do parafuso estão em contato com o material base.

        - **Tamanho Nominal Parafuso** — O Tamanho nominal do parafuso segundo o sistema métrico.

        - **Coeficiente de torque (Fator K)** — Coeficiente entre o torque aplicado e a força axial resultante no parafuso. É função das características de atrito dos materiais (acabamento superficial, revestimentos etc.). Esse valor resulta de uma combinação dos fatores de atrito geométrico, na rosca e na face de apoio.
        Um valor comumente usado é 0,2. O método mais confiável de determinar esse valor é através de testes. Contudo, como este software não é para uso em procedimentos críticos, o valor padrão foi assumido.''')

        st.markdown('### 📐 Premissas')
        st.markdown('''
        - As roscas estão completamente engajadas. O comprimento de engajamento é igual à espessura da peça e ao comprimento da rosca do parafuso.
        - O parafuso é completamente roscado.
        - A resistência ao cisalhamento do aço carbono é igual a 60% da resistência à tração:
        - A resistência ao cisalhamento do aço inoxidável é igual a 55% da resistência à tração:
        - O material do parafuso é mais resistente que o material base.
        - Parafusos de aço inoxidável com limite de escoamento de 1.241 MPa.
        - Os parafusos são rosqueados diretamente no material base (sem inserto).
        - Roscas classe 2A.
        - 65% da carga de tração é usada para cálculo do torque de montagem
        - Mínimo de 3 filetes de rosca engajados.
        - Coeficiente de torque (K) = 0,2
        ''')

        st.markdown('### 🔩 Resistências ao Cisalhamento')
        st.table(df_cisalhamento.reset_index(drop=True))

        
if __name__ == "__main__":
    main()