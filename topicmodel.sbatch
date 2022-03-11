#!/bin/bash
#SBATCH -A nkachild
#SBATCH --job-name=topicModel
#SBATCH --output=topicModel.out
#SBATCH --error=topicModel.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=22
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chris.thornton@ncl.ac.uk
#SBATCH --mem-per-cpu=5000

echo Starting job
module load Python
source $HOME/NLP/nlp-env/bin/activate
python3 topicModellingParamScan.py
echo Finishing job

