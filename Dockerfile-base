FROM jupyter/base-notebook
add envs/shunPykeR.yml ./shunPykeR.yml
add notebooks/shunPykeR_guide.ipynb shunPykeR_guide.ipynb
# dependency annoy needs to be built, and base-notebook does not have GCC
USER root
RUN apt-get update --yes && apt-get install g++ --yes --no-install-recommends &&  rm -rf /var/lib/apt/lists/*
USER ${NB_UID}
RUN mamba env create -f shunPykeR.yml
# inspired by https://medium.com/@nrk25693/how-to-add-your-conda-environment-to-your-jupyter-notebook-in-just-4-steps-abeab8b8d084
# This adds this env as a dropdown option in jupyter
RUN mamba install -n shunPykeR -c anaconda ipykernel && mamba install -n base nb_conda_kernels && mamba clean -afy
# do we need dpeerlab's fork? If not, use pip install magic-impute
# RUN wget https://github.com/dpeerlab/magic/archive/refs/tags/v0.1.1.tar.gz && \
#     tar xzf v0.1.1.tar.gz && \
#     ls && cd magic-0.1.1/ && \
#     /opt/conda/envs/shunPykeR/bin/pip install .
