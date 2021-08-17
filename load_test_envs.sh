#!/bin/sh
export $(grep -v '^#' ./envs/test.env | xargs)