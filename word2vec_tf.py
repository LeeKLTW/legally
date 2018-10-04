# work in progress

import collections 
import math
import os
import sys
import argparse
import random
import urllib
from tempfile import gettempdir
import zipfile
import numpy as np
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
import matplotlib.pyplot as plt 

current_path = os.path.dirname(os.path.realpath(sys.argv[0]))


parser = argparse.ArgumentParser()
parser.add_argument('--log_dir',
    type=str,
    default=os.path.join(current_path,'log'),
    help='The log directory for TensorBoard Summeries.')

FLAGS, unparsed = parser.parse_known_args()

if not os.path.exists(FLAGS.log_dir):
    os.makedirs(FLAGS.log_dir)
    
url = 'http://mattmahoney.net/dc/'

def maybe_download(filename, expected_bytes):
    local_filename = os.path.join(gettempdir(), filename)
    if not os.path.exists(local_filename):
        local_filename, _ = urllib.request.urlretrieve(url + filename,local_filename)
    statinfo = os.stat(local_filename)
    if statinfo.st_size == expected_bytes:
        print('Found and verified', filename)
    else:
        print(statinfo.st_size)
        raise Exception('Failed to verify ' + local_filename +'. Can you get to it with a browser?')
    return local_filename

def read_data(filename):
    with zipfile.ZipFile(filename) as f:
        data = tf.compat.as_str(f.read(f.namelist()[0])).split()
    return data

filename = maybe_download('text8.zip', 31344016)
vocabulary = read_data(filename)
print('Data size', len(vocabulary))

def build_dataset(words,n_words):
    '''
    count : word count
    dictionary: word to index
    data :indexed_sentence
    reversed_dictionary : index to word
    '''
    count = [['UNK',-1]]
    count.extend(collections.Counter(words).most_common(n_words-1))
    dictionary = dict()
    for word,_ in count:
        dictionary[word] = len(dictionary)
    data = list()
    unk_count = 0
    for word in words:
        index = dictionary.get(word,0)
        if index == 0:
            unk_count+=1
        data.append(index)
    count[0][1] = unk_count
    reversed_dictionary = dict(zip(dictionary.values(),dictionary.keys()))
    return data, count, dictionary, reversed_dictionary

vocabulary_size = 50000
data, count, dictionary, reversed_dictionary=build_dataset(vocabulary,vocabulary_size)

print('Most common words (+UNK)', count[:5])
print('\n')
print('Sample data', data[:10], [reversed_dictionary[i] for i in data[:10]])
print('Sample data', data[:8], '\n',[reversed_dictionary[i] for i in data[:8]])

data_index = 0
def generate_batch(data,batch_size, num_skips, skip_window):
    global data_index
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size,1),dtype=np.int32)
    span = 2 * skip_window+1 #???
    buffer = collections.deque(maxlen=span)
    if data_index + span > len(data):
        data_index = 0
    buffer.extend(data[data_index:data_index+span])
    data_index += span
    for i in range(batch_size//num_skips):
        context_words = [w for w in range(span) if w!=skip_window]
        words_to_use = random.sample(context_words,num_skips)
        for j,context_word in enumerate(words_to_use):
            batch[i*num_skips+j]=buffer[skip_window]
            labels[i*num_skips+j,0]=buffer[context_word]
        if data_index == len(data):
            buffer.extend(data[0:span])
            data_index = span
        else:
            buffer.append(data[data_index])
            data_index+=1
    data_index = (data_index+len(data)-span)%len(data)
    return batch,labels
batch = np.ndarray(shape=(16),dtype=np.int32)
labels = np.ndarray(shape=(16,1),dtype=np.int32)
span = 2 * 1+1
buffer = collections.deque(maxlen=span)
buffer.extend(data_[data_index:data_index+span])
for i in range(8):
    context_words = [w for w in range(span) if w!=1]
    words_to_use = random.sample(context_words,num_skips)

batch, labels = generate_batch(data=[5234, 3081, 12, 6, 195, 2, 3134, 46],
                               batch_size=16,num_skips=2,skip_window=1)
for i in range(16):
    print(batch[i],reversed_dictionary[batch[i]],'->',labels[i,0],reversed_dictionary[labels[i,0]])

batch, labels = generate_batch(data,batch_size=8, num_skips=2, skip_window=1)
for i in range(8):
    print(batch[i],reversed_dictionary[batch[i]],'->',labels[i,0],reversed_dictionary[labels[i,0]])

batch_size = 128
embedding_size = 128
skip_window = 1
num_skips = 2
num_sampled = 64
valid_size = 16
valid_window = 100
valid_examples = np.random.choice(valid_window,valid_size,replace=False)

tf.reset_default_graph()
graph = tf.Graph()
with graph.as_default():
    with tf.name_scope('inputs'):
        train_inputs = tf.placeholder(tf.int32,shape=[batch_size])
        train_labels = tf.placeholder(tf.int32,shape=[batch_size,1])
        valid_dataset = tf.constant(valid_examples,dtype=tf.int32)
        
    with tf.name_scope('embeddings'):
        embeddings = tf.Variable(tf.random_uniform([vocabulary_size,embedding_size],-1.0,1.0))
        embed = tf.nn.embedding_lookup(embeddings,train_inputs)
        
    with tf.name_scope('weights'):
        nce_weights = tf.Variable(tf.truncated_normal([vocabulary_size,embedding_size],stddev=1.0/math.sqrt(embedding_size)))
    with tf.name_scope('biases'):
        nce_biases = tf.Variable(tf.zeros([vocabulary_size]))
    
    with tf.name_scope('loss'):
        loss = tf.reduce_mean(tf.nn.nce_loss(weights=nce_weights,biases=nce_biases,
                                             labels=train_labels,inputs=embed,num_sampled=num_sampled,
                                             num_classes=vocabulary_size))
    tf.summary.scalar('loss',loss)
    
    with tf.name_scope('optimizer'):
        optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)
    
    norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings),1,keepdims=True))
    normalized_embeddings = embeddings/norm
    valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings,valid_dataset)
    similarity = tf.matmul(valid_embeddings,normalized_embeddings,transpose_b=True)
    merged = tf.summary.merge_all()
    saver = tf.train.Saver()

vocabulary_size = 100
num_steps = int(1e3)+1
with tf.Session(graph=graph) as sess:
    writer = tf.summary.FileWriter('./log',sess.graph)
    tf.global_variables_initializer().run()
    print('Initialized')
    
    average_loss = 0
    for step in range(num_steps):
        batch_input, batch_labels= generate_batch(batch_size,num_skips,skip_window)
        feed_dict = {train_inputs:batch_input,train_labels:batch_labels}
        
        run_metadata = tf.RunMetadata()
        
        _, summary, loss_val = sess.run([optimizer,merged,loss],feed_dict=feed_dict,run_metadata=run_metadata)
        average_loss += loss_val
        writer.add_summary(summary,step)
        if step == (num_steps-1):
            writer.add_run_metadata(run_metadata,'step{}'.format(step))
        if step % 100 ==0:
            if step>0:
                average_loss /= 2000
            print('Average loss at step', step, ':',average_loss)
            average_loss = 0
            
    final_embeddings = normalized_embeddings.eval()
    print('writing')
    with open('log' + '/metadata.tsv', 'w') as f:
        for i in range(vocabulary_size):
            f.write(reversed_dictionary[i] + '\n')
            saver.save(sess, os.path.join('log', 'model.ckpt'))
            config = projector.ProjectorConfig()
            embedding_conf = config.embeddings.add()
            embedding_conf.tensor_name = embeddings.name
            embedding_conf.metadata_path = os.path.join('log', 'metadata.tsv')
            projector.visualize_embeddings(writer, config)
            if i % 10 ==0:
                print(i)
    writer.close()
    print('finish')

def plot_with_labels(low_dim_embs, labels):
    assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
    plt.figure(figsize=(18, 18))  # in inches
    for i, label in enumerate(labels):
        x, y = low_dim_embs[i, :]
        plt.scatter(x, y)
        plt.annotate(
        label,
        xy=(x, y),
        xytext=(5, 2),
        textcoords='offset points',
        ha='right',
        va='bottom')
    plt.show()

tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=250, method='exact')
low_dim_embs = tsne.fit_transform(final_embeddings[:plot_only, :])

labels = [reversed_dictionary[i] for i in range(plot_only)]
plot_with_labels(low_dim_embs, labels)

