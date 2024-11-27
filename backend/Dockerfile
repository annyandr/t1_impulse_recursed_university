FROM continuumio/miniconda
WORKDIR /codes
COPY ./ ./
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

EXPOSE 5003
# The code to run when container is started:
ENTRYPOINT ["conda", "run", "-n", "myenv", "python3", "codes/app.py"]