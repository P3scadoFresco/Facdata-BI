import pandas as pd
from src.output.tableau_exporter import TableauExporter

def prepare_painel_6_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_6 = df_processed.copy()

    df_painel_6['Clientes'] = df_painel_6.get('Clientes', df_painel_6.get('cliente'))

    df_demand_type = df_painel_6.groupby('type').agg(
        total_cards=('card_id','count')
    ).reset_index()

    df_demand_type['pct_total'] = (
        df_demand_type['total_cards'] /
        df_demand_type['total_cards'].sum()
    ) * 100

    exporter.export_to_csv(df_demand_type,'painel_6_demand_type.csv')

    df_demand_subcategory = df_painel_6.groupby('subcategory').agg(
        total_cards=('card_id','count')
    ).reset_index().sort_values(by='total_cards',ascending=False)

    exporter.export_to_csv(df_demand_subcategory,'painel_6_demand_subcategory.csv')

    df_demand_client = df_painel_6.groupby('Clientes').agg(
        total_cards=('card_id','count')
    ).reset_index().sort_values(by='total_cards',ascending=False)

    exporter.export_to_csv(df_demand_client,'painel_6_demand_client.csv')

    df_weekly_demand = df_painel_6.groupby(
        df_painel_6['created_at'].dt.to_period('W')
    ).agg(
        cards_criados=('card_id','count')
    ).reset_index()

    exporter.export_to_csv(df_weekly_demand,'painel_6_weekly_demand.csv')

    print("Dados para Painel 6 preparados.")
    return df_painel_6
