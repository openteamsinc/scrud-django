# scrud-django
A Django application for SCRUD REST services. Semantic REST API generation.

## Get Started

### Get prepared to run tests and the demo application

```bash
cd docker
conda env create -f environment-dev.yml
conda activate scrud-django
cd ..
make develop
make migrate
```
### Confirm setup

```bash
make run_tests
```

### Start the demo application

```bash
cd demo
python manage.py runserver
```


