#!/bin/bash
#SBATCH -A nkachild
#SBATCH --job-name=msnet
#SBATCH --output=msnet.out
#SBATCH --error=msnet.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chris.thornton@ncl.ac.uk
#SBATCH --mem-per-cpu=3000

echo Starting job
module load Python
source $HOME/NLP/nlp-env/bin/activate
python3 mumsnetGetData.py
echo Finishing job

