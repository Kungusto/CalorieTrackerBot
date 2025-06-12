from sqlalchemy import select, insert, update
from src.schemas.users import User
from src.models.users import UsersORM


class UsersRepository:
    def __init__(self, session):
        self.session = session


    async def get_user(self, user_id): 
        query = (
            select(UsersORM)
            .filter_by(user_id=user_id)
        )
        model = await self.session.execute(query)
        result = model.scalar_one()
        return User.model_validate(result, from_attributes=True)


    async def new_user(self, data):
        insert_stmt = insert(UsersORM).values(**data.model_dump()).returning(UsersORM)
        model = await self.session.execute(insert_stmt)
        return User.model_validate(model.scalar_one(), from_attributes=True)

    async def update_user_data(self, user_id, data):
        update_stmt = (
            update(UsersORM)
            .filter_by(user_id=user_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(UsersORM)
        )
        model = await self.session.execute(update_stmt)
        result = model.scalar_one() 
        return User.model_validate(result, from_attributes=True)

    async def is_new(self, user_id):
        query = select(UsersORM).filter_by(user_id=user_id)
        model = await self.session.execute(query)
        try:
            model.scalar_one()
            return False
        except Exception:
            return True
