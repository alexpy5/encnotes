# encnotes

Encnotes - зашифрованные записки. Приложение на Python, с помощью
модуля cryptography создает зашифрованные сообщения и заносит их в базу данных.
Ключ для расшифровки содержится в ссылке. Приложение подготовлено для развертывания
на хостинге [Heroku](https://www.heroku..com). Не забудьте указать переменные среды.

[Демонстрация работы приложения](https://encnote.herokuapp.com)

## Переменные среды

- FLASK_APP=encnotes.py (сам скрипт)
- SECRET_KEY=super-mega-password (ключ для генерации подписей и токенов)
- (Unix) DATABASE_URL=sqlite:////home/user/Python/encnotes/app.db (адрес базы данных)
- (Windows) DATABASE_URL=sqlite:///D:\Python\encnotes\app.db
