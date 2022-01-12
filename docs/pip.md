```sh

sudo pip3 install -U pip
sudo pip3 install six==1.16.0
sudo pip3 install cython==0.29.26
sudo pip3 install protobuf>=3.3.0 patsy>=0.5

sudo pip3 install numpy==1.19.4 scipy==1.5.4 scikit-learn==0.24.0

sudo pip3 install markupsafe==2.0.1 flask==2.0.2 flask_cors==3.0.10
sudo pip3 install zerorpc==0.6.3 psutil==5.8.0

sudo pip3 install traitlets==4.3.2 jsonschema==2.6.0
sudo pip3 install jetson-stats

sudo pip3 install --global-option=build_ext --global-option="-I/usr/local/cuda/include/" --global-option="-L/usr/local/cuda/lib" pycuda==2020.1

# see third-party/resources
# sudo pip3 install statsmodels==0.12.2
```
