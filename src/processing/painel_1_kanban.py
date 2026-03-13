import pandas as pd
from src.output.tableau_exporter import TableauExporter
from datetime import datetime, timedelta

def prepare_painel_1_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_1 = df_processed.copy()

    df_painel_1 = df_painel_1[
        (df_painel_1['closed_at'].isna()) |
        (df_painel_1['closed_at'].dt.date == datetime.now().date())
    ].copy()

    df_painel_1['time_in_current_column_hours'] = df_painel_1.apply(
        lambda row: (datetime.now() - row['last_modified']).total_seconds() / 3600
        if pd.isna(row['closed_at']) else 0, axis=1
    )

    kpis_kanban = {
        'total_cards': len(df_painel_1),
        'cards_em_risco': df_painel_1[df_painel_1['status_sla'].isin(['Crítico', 'Aviso'])].shape[0],
        'cards_ok': df_painel_1[df_painel_1['status_sla'] == 'OK'].shape[0],
        'cards_fechados_hoje': df_painel_1[df_painel_1['closed_at'].dt.date == datetime.now().date()].shape[0]
    }

    df_kpis = pd.DataFrame([kpis_kanban])
    exporter.export_to_csv(df_kpis, 'painel_1_kpis_kanban.csv')

    df_horas_owner = df_painel_1.groupby('owner').agg(
        total_horas_investidas=('total_cycle_time', 'sum'),
        cards_ativos=('card_id', 'count'),
        cards_em_risco=('status_sla', lambda x: (x.isin(['Crítico', 'Aviso'])).sum())
    ).reset_index()

    exporter.export_to_csv(df_horas_owner, 'painel_1_horas_owner.csv')

    exporter.export_to_csv(df_painel_1, 'painel_1_kanban_live_cards.csv')

    print("Dados para Painel 1 preparados.")
    return df_painel_1
