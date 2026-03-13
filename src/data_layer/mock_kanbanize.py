import pandas as pd
import random
from faker import Faker
from datetime import timedelta

fake = Faker()

class MockKanbanizeData:

    def generate_mock_data(self):

        owners = ["Ana","Carlos","Marina","João","Lucas","Fernanda"]

        activity_types = [
            "Data Engineering",
            "Data Analysis",
            "Bug Fix",
            "Feature",
            "Research"
        ]

        columns_kanban = [
            "Backlog",
            "To Do",
            "In Progress",
            "Review",
            "QA",
            "Done"
        ]


        types = [
            "Bug",
            "Feature",
            "Improvement",
            "Data Request",
            "Support"
        ]

        subcategories = ["Pipeline","Dashboard","ETL","Infra","Analytics"]

        priorities = ["Low","Medium","High","Critical"]

        clientes = [
            "Banco XP",
            "Empresa Y",
            "Startup Z",
            "Cliente Interno"
        ]

        block_reasons = [
            "Dependência externa",
            "Aguardando cliente",
            "Bug em sistema",
            "Infraestrutura",
            "Prioridade alterada"
        ]


        rows = []

        for i in range(200):

            created_at = fake.date_time_between(start_date="-90d", end_date="-5d")

            created_week = created_at.isocalendar()[1]

            last_modified = created_at + timedelta(hours=random.randint(1,48))

            closed = random.choice([True, False])

            if closed:
                closed_at = created_at + timedelta(hours=random.randint(5,120))
            else:
                closed_at = None

            size = random.choice([4,8,16,24,40])

            total_cycle_time = random.randint(5,120)

            deadline = created_at + timedelta(hours=random.randint(40,120))

            horas_restantes_sla = random.randint(-20,50)

            desvio_horas = total_cycle_time - size

            is_blocked = random.choice([True, False])

            total_block_time = random.randint(0,48) if is_blocked else 0

            status_sla = random.choice([
                "No prazo",
                "Em risco",
                "Atrasado"
            ])

            reopened_count = random.randint(0,3)

            row = {

                "card_id": i+1,
                "card_title": fake.sentence(nb_words=4),

                "owner": random.choice(owners),

                "type": random.choice(types),

                "activity_type": random.choice(activity_types),

                "subcategory": random.choice(subcategories),

                "priority": random.choice(priorities),

                "Cliente": random.choice(clientes),

                "historical_column": random.choice(columns_kanban),

                "block_reason": random.choice(block_reasons),

                "reopened_count": reopened_count,

                "created_at": created_at,
                "last_modified": last_modified,
                "closed_at": closed_at,

                "created_week": created_week,

                "deadline": deadline,

                "size": size,

                "total_cycle_time": total_cycle_time,

                "horas_restantes_sla": horas_restantes_sla,

                "desvio_horas": desvio_horas,

                "status_sla": status_sla,

                "is_blocked": is_blocked,

                "total_block_time": total_block_time,

                "valor_projeto": random.randint(5000,50000)

            }

            rows.append(row)

        return pd.DataFrame(rows)
