# Clinton: layers = 3; size = 1024
# Trump: layers = 2; size = 512

TRAIN_DIR="checkpoints"
DATA_DIR="data"
SIZE=5
NUM_LAYERS=1
STEPS_PER_CHECKPOINT=50

SRC_NAME="en"
SRC_VOCAB_SIZE=100
TGT_NAME="fr"
TGT_VOCAB_SIZE=100

LEARNING_RATE=0.5

python translate.py --decode --train_dir $TRAIN_DIR --size=$SIZE --num_layers=$NUM_LAYERS --steps_per_checkpoint=$STEPS_PER_CHECKPOINT --data_dir $DATA_DIR --learning_rate=$LEARNING_RATE --src_name $SRC_NAME --tgt_name $TGT_NAME --src_vocab_size=$SRC_VOCAB_SIZE --tgt_vocab_size=$TGT_VOCAB_SIZE
