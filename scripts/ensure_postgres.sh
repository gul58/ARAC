#!/bin/bash
sudo pg_ctlcluster 16 main start 2>/dev/null || true
