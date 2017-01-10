# Clinton: layers = 3; size = 1024
# Trump: layers = 2; size = 512

TRAIN_DIR="checkpoints"
DATA_DIR="data"
SIZE=5
NUM_LAYERS=1
STEPS_PER_CHECKPOINT=50

C1_NAME="en"
C1_VOCAB_SIZE=100
C2_NAME="fr"
C2_VOCAB_SIZE=100

LEARNING_RATE=0.5

python translate.py --train_dir $TRAIN_DIR --size=$SIZE --num_layers=$NUM_LAYERS --steps_per_checkpoint=$STEPS_PER_CHECKPOINT --data_dir $DATA_DIR --learning_rate=$LEARNING_RATE --c1_name $C1_NAME --c2_name $C2_NAME --c1_vocab_size=$C1_VOCAB_SIZE --c2_vocab_size=$C2_VOCAB_SIZE
