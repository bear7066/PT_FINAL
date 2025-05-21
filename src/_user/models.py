from redis_om import HashModel, Field

class User(HashModel):
    username: str
    usermail: str = Field(index=True)
    password: str

    @classmethod
    async def isExisted(cls, usermail: str):
        existed = list(User.find(User.usermail == usermail))
        return True if existed else False






# user = User(username="testuser", password_hash="123456hash").save()
# fetched = User.get(user.pk)
# print(fetched.username)
# User.delete(user.pk)