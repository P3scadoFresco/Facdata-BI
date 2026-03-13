import pandas as pd
from src.output.tableau_exporter import TableauExporter

def prepare_painel_7_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_7 = df_processed.copy()

    df_column_time = df_painel_7.groupby('historical_column').agg(
        tempo_total=('total_cycle_time','sum'),
        num_cards=('card_id','count')
    ).reset_index()

    df_column_time['tempo_medio'] = (
        df_column_time['tempo_total'] /
        df_column_time['num_cards']
    )

    exporter.export_to_csv(df_column_time,'painel_7_column_time.csv')

    df_waiting_cards = df_painel_7[
        (df_painel_7['closed_at'].isna()) &
        (df_painel_7['total_cycle_time'] > df_painel_7['total_cycle_time'].mean())
    ]

    exporter.export_to_csv(df_waiting_cards,'painel_7_waiting_cards.csv')

    print("Dados para Painel 7 preparados.")
    return df_painel_7
