import os

class TableauExporter:

    def __init__(self):
        self.output_dir = "output_data"
        os.makedirs(self.output_dir, exist_ok=True)

    def export_to_csv(self, dataframe, filename):

        path = os.path.join(self.output_dir, filename)

        dataframe.to_csv(path, index=False)

        print(f"Arquivo gerado: {path}")
