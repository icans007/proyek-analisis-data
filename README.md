# E-Commerce Public Dataset

## Setup Environment - Anaconda

conda create --name e-commerce python=3.9
conda activate e-commerce
pip install -r requirements.txt

## Setup Environment - Shell/Terminal

mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt

## Run Streamlit App

streamlit run dashboard/dashboard.py

## Run Live Streamlit App

...