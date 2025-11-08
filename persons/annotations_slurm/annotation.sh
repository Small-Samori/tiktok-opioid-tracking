#!/bin/bash
#SBATCH --job-name=gpt_annotation
#SBATCH --output=./slurm_outputs/output_%j.log
#SBATCH --error=./slurm_errors/error_%j.err
#SBATCH --time=48:00:00
#SBATCH --mem=16G
#SBATCH --partition=rbaltman

TIKTOK_FOLDER=$OAK/samori/tiktok
COMMENT_FOLDER=$TIKTOK_FOLDER/comments
PERSONS_FOLDER=$TIKTOK_FOLDER/persons


source $GROUP_HOME/samori/miniconda3/condabin/conda lda_env2
python ./annotation.py $COMMENT_FOLDER/cleaned/comments_5_cleaned.csv $PERSONS_FOLDER