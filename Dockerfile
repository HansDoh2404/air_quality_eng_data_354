FROM apache/airflow:2.10.4

# Utilisation de l'utilisateur airflow
USER airflow

# Installation des packages nécéssaires pour le bon fonctionnement de mongodb
RUN python3 -m pip install pymongo apache-airflow-providers-mongo prophet