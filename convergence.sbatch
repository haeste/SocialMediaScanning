#!/bin/bash
#SBATCH -A nkachild
#SBATCH --job-name=convergence
#SBATCH --output=convergence.out
#SBATCH --error=convergence.err
#SBATCH --time=10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chris.thornton@ncl.ac.uk
#SBATCH --mem-per-cpu=5000

echo Starting job
module load Python
source $HOME/NLP/nlp-env/bin/activate
python3 calculateConvergence.py
echo Finishing job

