#!/usr/bin/env python
\\\"Example: Run SFT stage\\\"\"

from training.training_pipeline import TrainingPipeline

if __name__ == '__main__':
    pipeline = TrainingPipeline()
    pipeline.run_stage('sft')

