import pandas as pd
from src.output.tableau_exporter import TableauExporter
import os
from dotenv import load_dotenv

load_dotenv()

def prepare_painel_2_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_2 = df_processed.copy()

    owner_weekly_capacity = int(os.getenv('OWNER_WEEKLY_CAPACITY', 40))

    df_owner_monthly_hours = df_painel_2[
        df_painel_2['created_at'].dt.month == pd.Timestamp.now().month
    ].groupby('owner').agg(
        total_horas_investidas=('total_cycle_time', 'sum'),
        total_horas_estimadas=('total_cycle_time', 'sum'),
        cards_concluidos=('card_id', lambda x: x[df_painel_2.loc[x.index, 'closed_at'].notna()].count()),
        cards_ativos=('card_id', lambda x: x[df_painel_2.loc[x.index, 'closed_at'].isna()].count())
    ).reset_index()

    df_owner_monthly_hours['utilizacao_pct'] = (
        df_owner_monthly_hours['total_horas_investidas'] / (owner_weekly_capacity * 4)
    ) * 100

    df_owner_monthly_hours['horas_folga_debito'] = (
        (owner_weekly_capacity * 4) - df_owner_monthly_hours['total_horas_investidas']
    )

    exporter.export_to_csv(df_owner_monthly_hours, 'painel_2_owner_monthly_hours.csv')

    df_owner_activity_hours = df_painel_2[
        df_painel_2['created_at'].dt.month == pd.Timestamp.now().month
    ].groupby(['owner', 'activity_type']).agg(
        horas_investidas=('total_cycle_time', 'sum')
    ).reset_index()

    exporter.export_to_csv(df_owner_activity_hours, 'painel_2_owner_activity_hours.csv')

    df_desvio = df_painel_2[df_painel_2['closed_at'].notna()].copy()

    df_desvio['desvio_horas_pct'] = 0

    exporter.export_to_csv(
    df_desvio[['card_id','owner','total_cycle_time','desvio_horas_pct','subcategory']],
    'painel_2_desvio_estimado_real.csv'
)

    print("Dados para Painel 2 preparados.")
    return df_painel_2
