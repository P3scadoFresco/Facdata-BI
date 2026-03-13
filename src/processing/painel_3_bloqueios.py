import pandas as pd
from src.output.tableau_exporter import TableauExporter

def prepare_painel_3_data(df_processed: pd.DataFrame, exporter: TableauExporter):

    df_painel_3 = df_processed.copy()

    df_alerts_sla = df_painel_3[
        df_painel_3['status_sla'].isin(['Crítico','Aviso','Violado']) &
        df_painel_3['closed_at'].isna()
    ].copy()

    df_alerts_sla = df_alerts_sla[
    ['card_id','owner','status_sla']
]


    exporter.export_to_csv(df_alerts_sla, 'painel_3_alerts_sla.csv')

    df_blocked_cards = df_painel_3[df_painel_3['is_blocked'] == True].copy()

    df_blocked_cards['tempo_bloqueado_dias'] = df_blocked_cards['total_block_time'] / 24

    df_blocked_cards = df_blocked_cards[
        ['card_id','card_title','owner','priority','block_reason','tempo_bloqueado_dias','status_sla','horas_restantes_sla']
    ]

    exporter.export_to_csv(df_blocked_cards, 'painel_3_blocked_cards.csv')

    df_top_block_reasons = df_blocked_cards.groupby('block_reason').agg(
        num_bloqueios=('card_id','count'),
        total_tempo_bloqueado=('tempo_bloqueado_dias','sum')
    ).reset_index().sort_values(by='num_bloqueios', ascending=False)

    df_top_block_reasons['pct_bloqueios'] = (
        df_top_block_reasons['num_bloqueios'] /
        df_top_block_reasons['num_bloqueios'].sum()
    ) * 100

    exporter.export_to_csv(df_top_block_reasons,'painel_3_top_block_reasons.csv')

    print("Dados para Painel 3 preparados.")
    return df_painel_3
