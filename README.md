 ## Продуктовый помощник - foodgram

---

 Создайте и поделитесь кулинарными шедеврами с миром. Публикуйте ваши рецепты, сохраняйте понравившиеся в избранное и следите за любимыми авторами. Наш сервис также предлагает удобный «список покупок» для составления списка продуктов, необходимых для приготовления ваших любимых блюд. С помощью него вы сможете легко создать файл с перечнем и количеством ингредиентов для покупки, который можно выгрузить в формате .txt.

 ***Для работы с проектом выполните следующие действия.***

 ```bash
git clone <project>
cd foodgram-project-react/infra/
# сделайте копию файла <.env.example> в <.env>
cp .env.example .env
 ```

**Docker**
 ```bash
docker compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
# Заполните базу тегами и ингредиентами:
docker-compose exec backend python manage.py import_tags
docker-compose exec backend python manage.py import_ingredients
```
***Тестовый пользователь и администратор***

Если выполнены все импорты в базу данных:
```bash
# Админ зона
http://127.0.0.1/admin
Login: admin
Password: admin

# Тестовый пользователь
http://127.0.0.1/
Email: kertiev1107@gmail.com
Password: kurjh111

# Документация
http://127.0.0.1/redoc
```
**POSTMAN**  
Для полноценного использования API необходимо выполнить регистрацию пользователя и получить токен. Инструкция для ***Postman:***

Получить токен для тестового пользователя если выполнены все импорты:  
POST http://127.0.0.1/api/auth/token/login/
```json
{
    "email": "kertievm04@gmail.com",
    "password": "qwerty0987"
}
```
Без импортов, регистрируем нового пользователя  
POST http://127.0.0.1/api/users/
```json
{
    "email": "murik11@gmail.com",
    "username": "User101",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "qwerty12345"
}
```
Получаем токен  
POST http://127.0.0.1/api/auth/token/login/
```json
{
    "password": "qwerty12345",
    "email": "amurik11@gmail.com"
}
```
Response status 200 OK ✅
```json
{
    "token": "epw4..."
}
```
Полученный токен вставляем Postman -> закладка Headers -> Key(Authorization) -> Value (Ваш токен в формате: Token epw4...)  

***Технологии:***  
Python 3.9, Django 3.2, DRF, Nginx, Docker, Docker-compose, Postgresql.  
<!-- 
***Cервер:***  
https://foodgram.ddnsking.com/  
https://foodgram.ddnsking.com/api/docs/ -->
