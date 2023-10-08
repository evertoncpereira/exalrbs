import streamlit as st
import pandas as pd
import mysql.connector


# Conectar ao MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="wacesso"
)


st.write("##             RELATÓRIO REFEIÇÕES")

st.sidebar.markdown('## FAÇA O O FILTRO')
# Criar widgets de entrada de data
data_inicial = st.sidebar.date_input("Selecione a data inicial:", format="DD/MM/YYYY")
data_final = st.sidebar.date_input("Selecione a data final:", format="DD/MM/YYYY")

# Filtrar os dados
if data_inicial is not None and data_final is not None:
    # Selecionar dados da tabela acesso
    cursor = conn.cursor()
    cursor.execute(
        "SELECT  b.OreMascara, a.HcrMatricula, a.HcrNomeUsuarioCracha, a.HcrDataHoraAcesso, c.Descricao, d.EqpDescricao FROM historicocracha as a left join organogramaestrutura as b on a.OreId = b.OreId left join categoria as c on a.Categoria = c.Id left join equipamento as d on a.EqpId=d.EqpId WHERE HcrDataHoraAcesso >= %s AND HcrDataHoraAcesso <= %s",
        (data_inicial, data_final)
    )

    # Exibir os dados
    dados = cursor.fetchall()
    df = pd.DataFrame(dados)
    df = df.rename(columns={0: 'CC'})
    df = df.rename(columns={1: 'MATRICULA'})
    df = df.rename(columns={2: 'NOME'})
    df = df.rename(columns={3: 'DATA/HORA'})
    df = df.rename(columns={4: 'MODALIDADE'})
    df = df.rename(columns={5: 'COLETOR     '})
    df["QTDE"] = 1
   # st.dataframe(df,hide_index=True)
    
   # st.dataframe(df,hide_index=True)  

    if df.empty:
        st.write("Selecione as datas")

    if not df.empty:     
         col1, col2 = st.columns(2)
         data = df.iloc[:, 3].dt.date
         hora = df.iloc[:, 3].dt.time

          # Crie duas novas colunas
         df["data"] = data
         df["hora"] = hora

         
         df["VALOR"] = df.iloc[:, 4].apply(lambda x: 24.50 if x == "PRESENCIAL" else 17.35)
         df["Vr Cons"] = 0      
         df["Vr Empre"] = 0 
         df["VALOR TOTAL"] = df["VALOR"]
         df = df[['CC', 'MATRICULA', 'NOME', 'data', 'hora', 'MODALIDADE', 'QTDE', 'VALOR', 'Vr Cons', 'Vr Empre','VALOR TOTAL','COLETOR     ']]
         df = df.sort_values(["NOME", "data"]).drop_duplicates(subset=["NOME", "data"], keep="last")
        # st.dataframe(df,hide_index=True)  


        
        # Crie um menu de seleção múltipla
         dfcoletor = pd.DataFrame ({"COLETOR": ["COLETOR 02", "COLETOR  TV", "COLETOR 01", "COLETOR PG"]})          
         coletores = st.sidebar.multiselect("Selecione os coletores", dfcoletor["COLETOR"].tolist())

        # Filtre o dataframe pelo coletor selecionado
         df_filtrado = df[df["COLETOR     "].isin(coletores)]


         #seleção múltipla Modalidae
         dfmodalidade = pd.DataFrame ({"MODALIDADE": ["PRESENCIAL", "HIBRIDO", "REMOTO", "ATIVIDADE EXTERNA"]})          
         modalidade = st.sidebar.multiselect("Selecione os coletores", dfmodalidade["MODALIDADE"].tolist())
       
         df_filtrado = df[df["MODALIDADE"].isin(modalidade)]

        # Exiba o dataframe filtrado
         st.dataframe(df_filtrado,hide_index=True)





         # Calcule a soma do campo valor
         soma_valor = df_filtrado.iloc[:, 7].sum()
         col1, col2 = st.columns(2)
         col1.markdown("TOTAL E REGISTROS:  **{}**.".format(df_filtrado.shape[0])) 
         col2.markdown("A soma do campo valor é **{}**.".format(soma_valor)) 

         botao_download = st.sidebar.download_button("Download Relatório", data=df_filtrado.to_csv(), file_name="dados.csv")

         # Se o botão for clicado, baixe o dataframe
         if botao_download:
            st.sidebar.write("O arquivo foi baixado com sucesso!",width=None)

#st.dataframe(df) 

# Fechar a conexão com o MySQL
conn.close()