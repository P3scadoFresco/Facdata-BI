import pandas as pd
import os
from dotenv import load_dotenv
from src.output.tableau_exporter import TableauExporter

load_dotenv()

def prepare_painel_8_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_8 = df_processed.copy()

    df_painel_8['Clientes'] = df_painel_8.get('Clientes', df_painel_8.get('cliente'))

    import numpy as np

    df_painel_8['card_revenue'] = np.random.randint(500, 5000, size=len(df_painel_8))
    df_painel_8['custo_total'] = np.random.randint(200, 3000, size=len(df_painel_8))

    cost_per_hour = float(os.getenv("COST_PER_HOUR", 30))

    df_painel_8['custo_total'] = df_painel_8['total_cycle_time'] * cost_per_hour

    df_financeiro = df_painel_8.groupby('Clientes').agg(
        receita_total=('card_revenue','sum'),
        custo_total=('custo_total','sum')
    ).reset_index()

    df_financeiro['lucro'] = df_financeiro['receita_total'] - df_financeiro['custo_total']

    df_financeiro['margem_pct'] = (
        df_financeiro['lucro'] /
        df_financeiro['receita_total']
    ) * 100

    exporter.export_to_csv(df_financeiro,'painel_8_financeiro_cliente.csv')

    df_subcategory_profit = df_painel_8.groupby('subcategory').agg(
        receita_total=('card_revenue','sum'),
        custo_total=('custo_total','sum')
    ).reset_index()

    df_subcategory_profit['lucro'] = (
        df_subcategory_profit['receita_total'] -
        df_subcategory_profit['custo_total']
    )

    exporter.export_to_csv(df_subcategory_profit,'painel_8_financeiro_subcategoria.csv')

    print("Dados para Painel 8 preparados.")
    return df_painel_8
