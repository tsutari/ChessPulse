#!/bin/bash
pip install -r requirements.txt
apt-get install -y stockfish 2>/dev/null || \
wget -q https://github.com/official-stockfish/Stockfish/releases/download/sf_17/stockfish-ubuntu-x86-64.tar -O /tmp/sf.tar && \
tar -xf /tmp/sf.tar -C /tmp && \
cp /tmp/stockfish/stockfish-ubuntu-x86-64 /opt/render/project/src/stockfish && \
chmod +x /opt/render/project/src/stockfish
