
# Yatube

Yatube is a social network for personal blogging of users. Users have the ability to publish their notes and photos. You can leave comments under other people's publications and create interest groups.
## Run Locally

At the first start, for the project to function, it is necessary to install a virtual environment and perform migrations:

    $ python -m venv venv
    $ source venv/Scripts/activate
    $ pip install -r requirements.txt
    $ python yatube_api/manage.py makemigrations
    $ python yatube_api/manage.py migrate

Create superuser for admin panel:

    $ python yatube_api/manage.py createsuperuser

Run server:

    $ python yatube_api/manage.py runserver

After launch, the project will be available at http://127.0.0.1:8000
## Related

Here are API for this project:

[Yatube-api](https://github.com/lordot/Yatube-api)

