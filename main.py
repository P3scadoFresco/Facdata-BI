print("teste")

import os
from dotenv import load_dotenv
from src.data_layer.mock_kanbanize import MockKanbanizeData
from src.processing.data_processor import DataProcessor
from src.output.tableau_exporter import TableauExporter

from src.processing.painel_1_kanban import prepare_painel_1_data
from src.processing.painel_2_carga_esforco import prepare_painel_2_data
from src.processing.painel_3_bloqueios import prepare_painel_3_data
from src.processing.painel_4_atividades import prepare_painel_4_data
from src.processing.painel_5_performance import prepare_painel_5_data
from src.processing.painel_6_demanda import prepare_painel_6_data
from src.processing.painel_7_gargalos import prepare_painel_7_data
from src.processing.painel_8_financeiro import prepare_painel_8_data

def main():

    load_dotenv()

    print("Iniciando pipeline...")

    mock_data_generator = MockKanbanizeData()
    df_raw = mock_data_generator.generate_mock_data()

    processor = DataProcessor(df_raw)
    df_processed = processor.process_data()

    exporter = TableauExporter()

    prepare_painel_1_data(df_processed, exporter)
    prepare_painel_2_data(df_processed, exporter)
    prepare_painel_3_data(df_processed, exporter)
    prepare_painel_4_data(df_processed, exporter)
    prepare_painel_5_data(df_processed, exporter)
    prepare_painel_6_data(df_processed, exporter)
    prepare_painel_7_data(df_processed, exporter)
    prepare_painel_8_data(df_processed, exporter)

    print("Pipeline concluído")

if __name__ == "__main__":
    main()
