### dev environment

Update lock

```shell
conda-lock lock --micromamba -f environment.yml --with-cuda 12.3
```

Create env

```shell
conda-lock install -n speech_to_gpt --micromamba
micromamba activate speech_to_gpt
python -m pip install -r requirements.txt
```

Note: you might need to install PyAudio
```
sudo apt install portaudio19-dev python3-pyaudio
```

# kill process in port

```shell
kill -9 $(lsof -t -i:8080)
```

