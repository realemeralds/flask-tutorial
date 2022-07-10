from app import *
user = User(teacher=True, username="yo", password="password", email="mattechane@gmail.com",
            qualis=3, age=17, subjects="[1, 2, 4]", bio="heyo! pls contact me", ratings=3)
print(user.prestige)
