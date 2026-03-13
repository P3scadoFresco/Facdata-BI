import pandas as pd
from src.output.tableau_exporter import TableauExporter

def prepare_painel_4_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_4 = df_processed.copy()

    df_activity_dist = df_painel_4.groupby('activity_type').agg(
        total_horas=('total_cycle_time','sum'),
        num_cards=('card_id','count')
    ).reset_index().sort_values(by='total_horas', ascending=False)

    df_activity_dist['pct_horas'] = (
        df_activity_dist['total_horas'] /
        df_activity_dist['total_horas'].sum()
    ) * 100

    exporter.export_to_csv(df_activity_dist,'painel_4_activity_distribution.csv')

    df_owner_activity_stack = df_painel_4.groupby(['owner','activity_type']).agg(
        horas_investidas=('total_cycle_time','sum')
    ).reset_index()

    exporter.export_to_csv(df_owner_activity_stack,'painel_4_owner_activity_stack.csv')

    df_avg_time_subcategory = df_painel_4[df_painel_4['closed_at'].notna()].groupby('subcategory').agg(
        tempo_medio_dias=('lead_time_days','mean'),
        tempo_min_dias=('lead_time_days','min'),
        tempo_max_dias=('lead_time_days','max'),
        desvio_padrao_dias=('lead_time_days','std')
    ).reset_index()

    exporter.export_to_csv(df_avg_time_subcategory,'painel_4_avg_time_subcategory.csv')

    df_weekly_evolution = df_painel_4.groupby(['created_week','activity_type']).agg(
        horas_investidas=('total_cycle_time','sum')
    ).reset_index()

    exporter.export_to_csv(df_weekly_evolution,'painel_4_weekly_activity_evolution.csv')

    print("Dados para Painel 4 preparados.")
    return df_painel_4
