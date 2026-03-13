import pandas as pd
from src.output.tableau_exporter import TableauExporter

def prepare_painel_5_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_5 = df_processed.copy()

    df_owner_performance = df_painel_5[df_painel_5['closed_at'].notna()].groupby('owner').agg(
        cards_concluidos=('card_id', 'count'),
        lead_time_medio=('lead_time_days', 'mean'),
        lead_time_mediano=('lead_time_days', 'median'),
        horas_totais=('total_cycle_time', 'sum')
    ).reset_index()

    exporter.export_to_csv(df_owner_performance, 'painel_5_owner_performance.csv')

    df_reopen_analysis = df_painel_5.groupby('owner').agg(
        total_cards=('card_id','count'),
        total_reaberturas=('reopened_count','sum')
    ).reset_index()

    df_reopen_analysis['taxa_reabertura_pct'] = (
        df_reopen_analysis['total_reaberturas'] /
        df_reopen_analysis['total_cards']
    ) * 100

    exporter.export_to_csv(df_reopen_analysis,'painel_5_reopen_analysis.csv')

    df_throughput_week = df_painel_5[df_painel_5['closed_at'].notna()].groupby(
        df_painel_5['closed_at'].dt.to_period('W')
    ).agg(
        cards_entregues=('card_id','count')
    ).reset_index()

    exporter.export_to_csv(df_throughput_week,'painel_5_throughput_week.csv')

    print("Dados para Painel 5 preparados.")
    return df_painel_5
