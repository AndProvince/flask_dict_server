from getpass import getpass
from app import create_app
from app.extensions import db
from app.models.user import User

def main():
    app = create_app()
    with app.app_context():  # <-- обязательный контекст приложения
        username = input("Введите имя пользователя: ")
        email = input("Введите email: ")
        password = getpass("Введите пароль: ")

        # Проверка на существование
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("❌ Пользователь с таким именем или email уже существует.")
            return

        # Создаём администратора
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"✅ Администратор {username} успешно создан.")

if __name__ == "__main__":
    main()
