import pandas as pd
from sqlalchemy import select, delete
from app.database import ApplicantsORM, new_session
import pandas as pd

def read_sheets(file_path):
    return pd.read_excel(file_path, sheet_name=None)

def write_sheets(data, file_path):
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for sheet, df in data.items():
            df.to_excel(writer, sheet_name=sheet, index=False)

def has_available_places(budget_places):
    return any(places > 0 for places in budget_places.values())

def get_next_priority(priority_level):
    return (priority_level % 256) + 1 # раз Госуслуги решили огранчить приоритет 256, то вот

def assign_abiturients(sheets, budget_places, priority_level):
    final_results = {sheet: pd.DataFrame(columns=["СНИЛС", "Приоритет", "Баллы", "Очный оригинал", "ЕПГУ"]) for sheet in sheets}
    progress = False

    for sheet, df in list(sheets.items()):
        available_places = budget_places[sheet]
        if available_places > 0 and not df.empty:
            for idx, row in df.iterrows():
                if row['Приоритет'] == priority_level:
                    if idx < available_places:
                        final_results[sheet] = pd.concat([final_results[sheet], pd.DataFrame([row])], ignore_index=True)
                        budget_places[sheet] -= 1
                        for other_sheet in sheets:
                            sheets[other_sheet] = sheets[other_sheet][sheets[other_sheet]['СНИЛС'] != row['СНИЛС']]
                            sheets[other_sheet] = sheets[other_sheet].reset_index(drop=True)

                        print(f"СНИЛС {row['СНИЛС']} -> {sheet}")
                        progress = True
                        break
        else:
            budget_places[sheet] = 0  # завершаю набор в конкурсную группу в случае недобора

    return final_results if progress else None

def process_admissions(sheets, budget_places):
    final_results = {sheet: pd.DataFrame(columns=["СНИЛС", "Приоритет", "Баллы", "Очный оригинал", "ЕПГУ"]) for sheet in sheets}
    priority_level = 1
    while has_available_places(budget_places):
        result = assign_abiturients(sheets, budget_places, priority_level)

        if result:
            for sheet, df in result.items():
                final_results[sheet] = pd.concat([final_results[sheet], df], ignore_index=True)
            priority_level = 1
        else:
            priority_level = get_next_priority(priority_level)

    return final_results