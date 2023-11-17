pip3 install --user --break-system-packages Nuitka
sudo apt install ccache patchelf

nuitka3 --standalone --follow-imports --include-plugin-files=./lib/*.py ./kopsrox.py 
