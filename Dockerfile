FROM jupyter/scipy-notebook
add envs/env.yaml ./env.yaml
add notebooks/shunPykeR_guide.ipynb shunPykeR_guide.ipynb
RUN mamba env create -f env.yaml
# inspired by https://medium.com/@nrk25693/how-to-add-your-conda-environment-to-your-jupyter-notebook-in-just-4-steps-abeab8b8d084
RUN mamba install -n shunPykeR -c anaconda ipykernel && mamba install -n base nb_conda_kernels #/opt/conda/envs/shunPykeR/bin/python -m ipykernel install --user --name=shunPykeR
# do we need dpeerlab's fork? If not, use pip install magic-impute
# RUN wget https://github.com/dpeerlab/magic/archive/refs/tags/v0.1.1.tar.gz && \
#     tar xzf v0.1.1.tar.gz && \
#     ls && cd magic-0.1.1/ && \
#     /opt/conda/envs/shunPykeR/bin/pip install .
