# _*_ coding:utf-8 _*_

import math
import os
import random
import sys
import time
import numpy as np
import tensorflow as tf

from tensorflow.models.rnn.translate import data_utils
from tensorflow.models.rnn.translate import seq2seq_model


tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 1024, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 3, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("en_vocab_size", 40000, "English vocabulary size.")
tf.app.flags.DEFINE_integer("fr_vocab_size", 40000, "French vocabulary size.")
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


class Decoder:
	def __init__(self, params):
		self.data_dir = params['data_dir']
		self.train_dir = params['train_dir']
		self.size = params['size']
		self.num_layers = params['n_layers']

		self.sess = tf.Session()
		# Create model and load parameters.
		self.model = self.create_model(self.sess, True)
		self.model.batch_size = 1  # We decode one sentence at a time.

		# Load vocabularies.
		en_vocab_path = os.path.join(self.data_dir,
					 "vocab%d.en" % FLAGS.en_vocab_size)
		fr_vocab_path = os.path.join(self.data_dir,
					 "vocab%d.fr" % FLAGS.fr_vocab_size)
		self.en_vocab, _ = data_utils.initialize_vocabulary(en_vocab_path)
		_, self.fr_vocab = data_utils.initialize_vocabulary(fr_vocab_path)


	def create_model(self, session, forward_only):
		"""Create translation model and initialize or load parameters in session."""
		dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
		model = seq2seq_model.Seq2SeqModel(
			FLAGS.en_vocab_size,
			FLAGS.fr_vocab_size,
			_buckets,
			self.size,
			self.num_layers,
			FLAGS.max_gradient_norm,
			FLAGS.batch_size,
			FLAGS.learning_rate,
			FLAGS.learning_rate_decay_factor,
			forward_only=forward_only,
			dtype=dtype)

		ckpt = tf.train.get_checkpoint_state(self.train_dir)
		if ckpt and tf.gfile.Exists(ckpt.model_checkpoint_path):
			print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
			model.saver.restore(session, ckpt.model_checkpoint_path)
			return model
		
		print("Checkpoint Directory not Found.")
		return None


	def decode(self, sentence):
	  
		# Get token-ids for the input sentence.
		token_ids = data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), self.en_vocab)
		# Which bucket does it belong to?
		bucket_id = min([b for b in xrange(len(_buckets))
			       if _buckets[b][0] > len(token_ids)])
		# Get a 1-element batch to feed the sentence to the model.
		encoder_inputs, decoder_inputs, target_weights = self.model.get_batch(
		  {bucket_id: [(token_ids, [])]}, bucket_id)
		# Get output logits for the sentence.
		_, _, output_logits = self.model.step(self.sess, encoder_inputs, decoder_inputs,
					       target_weights, bucket_id, True)
		# This is a greedy decoder - outputs are just argmaxes of output_logits.
		outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
		# If there is an EOS symbol in outputs, cut them at that point.
		if data_utils.EOS_ID in outputs:
			outputs = outputs[:outputs.index(data_utils.EOS_ID)]
	      
		# Print out French sentence corresponding to outputs.
		#print(" ".join([tf.compat.as_str(rev_fr_vocab[output]) for output in outputs]))
		translated_str = " ".join([tf.compat.as_str(self.fr_vocab[output]) for output in outputs])      
		
		return translated_str


	#####close tf session#####	
	def close_session(self):
		self.sess.close()


if __name__ == '__main__':
	
	params1_dict = {
			'data_dir'	: '/Users/bobby/Downloads/tensorflow/tensorflow/models/rnn/translate/trump_data_dir',
			'train_dir'	: '/Users/bobby/Downloads/tensorflow/tensorflow/models/rnn/translate/trump_checkpoint_dir', 
			'size'		: 256,
			'n_layers'	: 1
		}

	params2_dict = {
			'data_dir'	: '/Users/bobby/Downloads/tensorflow/tensorflow/models/rnn/translate/clinton_data_dir',
			'train_dir'	: '/Users/bobby/Downloads/tensorflow/tensorflow/models/rnn/translate/clinton_checkpoint_dir', 
			'size'		: 256,
			'n_layers'	: 1
		}

	dc1 = Decoder(params1_dict)
	dc2 = Decoder(params2_dict)
	
	####translate sentence###
	clinton_tweets = [
		'latest reckless idea from trump: gut rules on wall street, and leave middle-class families out to dry',
		'climate change is real, and threatens us all.',
		'america never stopped being great. we just need to make it work for everyone',
		'we need to make college more affordable',
		'it’s time to act on gun violence',
		'gun violence is ripping apart people’s lives'
	]

	for tweet in clinton_tweets:
		print(dc1.decode(tweet)	)

	####close the session####
	dc1.close_session()
	dc2.close_session()

