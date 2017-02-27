# _*_ coding:utf-8 _*_
import os
import numpy as np
import tensorflow as tf

from tensorflow.models.rnn.translate import seq2seq_model

import data_utils


tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 1024, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 3, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("src_vocab_size", 40000, "Source vocabulary size.")
tf.app.flags.DEFINE_integer("tgt_vocab_size", 40000, "Target vocabulary size.")
tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "/tmp", "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 200,
                            "How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_boolean("decode", False,
                            "Set to True for interactive decoding.")
tf.app.flags.DEFINE_boolean("self_test", False,
                            "Run a self-test if this is set to True.")
tf.app.flags.DEFINE_boolean("use_fp16", False,
                            "Train using fp16 instead of fp32.")

FLAGS = tf.app.flags.FLAGS

# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
_buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]


class Decoder(object):
    def __init__(self, params):
        self.data_dir = params['data_dir']
        self.train_dir = params['train_dir']
        self.size = params['size']
        self.num_layers = params['n_layers']
        self.src_name = params['src_name']
        self.tgt_name = params['tgt_name']

        self.sess = tf.Session()
        scope = "{}_{}".format(self.src_name, self.tgt_name)
        with tf.variable_scope(scope):
            self.model = self.create_model(self.sess, True, scope)

            self.model.batch_size = 1  # We decode one sentence at a time.

            # Load vocabularies.
            src_vocab_path = os.path.join(self.data_dir,
                                          "vocab{}.{}".format(FLAGS.tgt_vocab_size,
                                                              self.src_name))
            tgt_vocab_path = os.path.join(self.data_dir,
                                          "vocab{}.{}".format(FLAGS.tgt_vocab_size,
                                                              self.tgt_name))
            self.src_vocab, _ = data_utils.initialize_vocabulary(src_vocab_path)
            _, self.tgt_vocab = data_utils.initialize_vocabulary(tgt_vocab_path)

    def create_model(self, session, forward_only, scope_name):
        """Create translation model and initialize or load parameters in session."""
        dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
        model = seq2seq_model.Seq2SeqModel(
            FLAGS.src_vocab_size,
            FLAGS.tgt_vocab_size,
            _buckets,
            self.size,
            self.num_layers,
            FLAGS.max_gradient_norm,
            FLAGS.batch_size,
            FLAGS.learning_rate,
            FLAGS.learning_rate_decay_factor,
            forward_only=forward_only)

        ckpt = tf.train.get_checkpoint_state(self.train_dir)
        if ckpt and os.path.exists(ckpt.model_checkpoint_path):
            print "Reading model parameters from", ckpt.model_checkpoint_path
            model.saver.restore(session, ckpt.model_checkpoint_path)
            return model
        print "Checkpoint Directory not Found."
        return

    def decode(self, sentence):

        # Get token-ids for the input sentence.
        token_ids = data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), self.src_vocab)
        # Which bucket does it belong to?
        bucket_id = min([b for b in xrange(len(_buckets))
                         if _buckets[b][0] > len(token_ids)])
        # Get a 1-element batch to feed the sentence to the model.
        encoder_inputs, decoder_inputs, target_weights = self.model.get_batch(
            {bucket_id: [(token_ids, [])]}, bucket_id)
        # Get output logits for the sentence.
        _, _, output_logits = self.model.step(self.sess, encoder_inputs,
                                              decoder_inputs, target_weights,
                                              bucket_id, True)
        # This is a greedy decoder - outputs are just argmaxes of output_logits.
        outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
        # If there is an EOS symbol in outputs, cut them at that point.
        if data_utils.EOS_ID in outputs:
            outputs = outputs[:outputs.index(data_utils.EOS_ID)]

        # Print out French sentence corresponding to outputs.
        translated_str = " ".join([tf.compat.as_str(self.tgt_vocab[output]) for output in outputs])

        return translated_str

    def close_session(self):
        self.sess.close()


def main():
    c2t_params = {
        'data_dir': 'data/clinton_to_trump/',
        'train_dir': 'checkpoints/clinton_to_trump/',
        'size': 512,
        'n_layers': 2,
        'src_name': 'clinton',
        'tgt_name': 'trump'}

    t2c_params = {
        'data_dir': 'data/trump_to_clinton/',
        'train_dir': 'checkpoints/trump_to_clinton/',
        'size': 512,
        'n_layers': 2,
        'src_name': 'trump',
        'tgt_name': 'clinton'}

    params = t2c_params
    out_fname = 'output/t2c_test'
    in_fname = os.path.join(params['data_dir'], 'test.trump')

    dc = Decoder(params)
    
    count = 0
    with open(in_fname, 'r') as in_f:
        with open(out_fname, 'w') as out_f:
            for line in in_f:
                tweet = line.strip()
                translated = dc.decode(tweet)
                out_f.write(translated + '\n')
		count += 1
		if count % 10 == 0:
		    print count

    dc.close_session()


if __name__ == '__main__':
    main()
