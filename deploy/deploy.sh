#!/bin/sh
ssh johan@urdatorn 'mkdir -p ~/syncer/data/'
scp docker-compose.yml johan@urdatorn:syncer/
ssh johan@urdatorn 'cd ~/syncer/ && docker-compose up'

