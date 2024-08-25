from datetime import datetime, timedelta
from app.database import new_session, ApplicantsORM, CompetitionGroupsORM
from sqlalchemy import delete, exists, insert, select, update
import pandas as pd

class ApplicantsRepository:

    @classmethod
    async def add_or_update_user(cls, data: ApplicantsORM):
        async with new_session() as session:
            result = await session.execute(select(ApplicantsORM).filter_by(snils=data.snils))
            user_in_db = result.scalars().first()

            if user_in_db:
                if data.number is not None: user_in_db.number = data.number
                if data.exam_1 is not None: user_in_db.exam_1 = data.exam_1
                if data.exam_2 is not None: user_in_db.exam_2 = data.exam_2
                if data.exam_3 is not None: user_in_db.exam_3 = data.exam_3
                if data.personal_achivements is not None: user_in_db.personal_achivements = data.personal_achivements
                user_in_db.total_score = data.total_score
                user_in_db.last_update_on_server = data.last_update_on_server
                user_in_db.places = data.places
            else:
                session.add(data)
            await session.commit()

    @classmethod
    async def process_xlsx(cls, file_location: str):
        async with new_session() as session:
            df = pd.read_excel(file_location, dtype={7: str})
            for _, row in df.iterrows():
                new_applicant = ApplicantsORM(
                    name=row[1],
                    phone=row[5],
                    email=row[6],
                    snils=row[7],
                    contest_uuid=row[22],
                    competition_group=row[25],
                    type_of_places=row[28],
                    priority=row[30],
                    status=row[31],
                    original_docs=row[33],
                    epgu_docs=row[34],
                    vuz=row[35]
                )
                session.add(new_applicant)
            await session.commit()


    # @classmethod
    # async def get_contest_groups(cls):
    #     async with new_session() as session:
    #         unique_contests_query = select(ApplicantsORM.contest_uuid).where(ApplicantsORM.type_of_places == "Основные места в рамках КЦП").distinct()
    #         unique_contests_result = await session.execute(unique_contests_query)
    #         unique_contests_data = unique_contests_result.fetchall()
    #         for row in unique_contests_data:
    #             contest_uuid = row[0]
    #             contest_exists_query = select(exists().where(CompetitionGroupsORM.contest_uuid == contest_uuid))
    #             contest_exists_result = await session.execute(contest_exists_query)
    #             contest_exists = contest_exists_result.scalar()
    #             if not contest_exists:
    #                 insert_contest_query = insert(CompetitionGroupsORM).values(contest_uuid=contest_uuid)
    #                 await session.execute(insert_contest_query)
    #                 await session.commit()

    #         specialties_query = select(ApplicantsORM.competition_group).distinct()
    #         specialties_result = await session.execute(specialties_query)
    #         specialties_data = specialties_result.fetchall()
    #         specialties_dict = {row[0]: row[1] for row in specialties_data}

    #         return specialties_dict

    @classmethod
    async def create_preliminary_data(cls, specialties_dict):
        async with new_session() as session:
            with pd.ExcelWriter('vp.xlsx', engine='openpyxl') as writer:
                for speciality in specialties_dict.keys():
                    query = select(ApplicantsORM.snils, ApplicantsORM.priority, ApplicantsORM.total_score, ApplicantsORM.ochno, ApplicantsORM.epgu, ApplicantsORM.response).where(ApplicantsORM.agreement == "Бюджетные места", ApplicantsORM.speciality == speciality)
                    result = await session.execute(query)
                    data = result.fetchall()
                    df = pd.DataFrame(data, columns=["СНИЛС", "Приоритет", "Баллы", "Очный оригинал", "ЕПГУ"])
                    df.to_excel(writer, sheet_name=speciality, index=False)
