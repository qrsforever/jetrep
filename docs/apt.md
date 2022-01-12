sudo apt update

sudo apt install -y curl
sudo apt install -y python3-pip
sudo apt install -y libzmq3-dev

sudo apt install -y isc-dhcp-server
sudo apt install -y hostapd
sudo apt install -y dnsmasq

```
export CUDA_HOME=/usr/local/cuda

if [ ! -d $CUDA_HOME ]; then
  ln -s /usr/local/cuda-10.2 $CUDA_HOME
fi
export PATH=${CUDA_HOME}/bin:${PATH}
export CPATH=${CUDA_HOME}/include:${CPATH}
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
```
