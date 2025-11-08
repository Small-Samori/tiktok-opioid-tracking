#!/bin/bash

TIKTOK_FOLDER=$SCRATCH/samori/tiktok
COMMENT_FOLDER=$TIKTOK_FOLDER/comments
PERSONS_FOLDER=$TIKTOK_FOLDER/persons
MINICONDA_PATH=$GROUP_HOME/samori/miniconda3

# COMMENTS_FILE=$COMMENT_FOLDER/cleaned/comments_5_cleaned.csv
COMMENTS_FILE=$COMMENT_FOLDER/combined_comments_7.csv

ACTIVATE_ENV="source $MINICONDA_PATH/bin/activate tiktok_env2"
RUN_ANNOTATION="python ./annotation.py $COMMENTS_FILE $PERSONS_FOLDER"
# RUN_ANNOTATION="python ./annotation2.py $COMMENTS_FILE $PERSONS_FOLDER"

JOB_ID1=$(sbatch --parsable --partition=rbaltman --time 168:00:00 --mem 64G \
        --job-name gpt_annotation --wrap "$ACTIVATE_ENV;$RUN_ANNOTATION" \
        --output ./slurm_outputs/output_%j.log --error ./slurm_errors/error_%j.err \
        --mail-user iasamori@stanford.edu --mail-type=ALL)