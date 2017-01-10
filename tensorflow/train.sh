TRAIN_DIR="checkpoints"
DATA_DIR="data"
#SIZE="256"
SIZE="5"
NUM_LAYERS="1"
STEPS_PER_CHECKPOINT="50"

python translate.py --train_dir $TRAIN_DIR --size=$SIZE --num_layers=$NUM_LAYERS --steps_per_checkpoint=$STEPS_PER_CHECKPOINT --data_dir $DATA_DIR
