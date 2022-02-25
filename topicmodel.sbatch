#!/bin/bash
#SBATCH -A nkachild
#SBATCH --job-name=actigraph
#SBATCH --output=actigraph.out
#SBATCH --error=actigraph.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chris.thornton@ncl.ac.uk
#SBATCH --mem-per-cpu=5000

echo Starting job
module load Python
source $HOME/NLP/nlp-env/bin/activate
python3 topicModellingParamScan.py
echo Finishing job

