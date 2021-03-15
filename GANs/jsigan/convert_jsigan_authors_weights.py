# Copyright (c) 2017 Sony Corporation. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

import numpy as np

import nnabla as nn
from nnabla.parameter import get_parameter_or_create
from tensorflow.python import pywrap_tensorflow

parser = argparse.ArgumentParser(description='Convert TF TecoGAN weights to NNabla format')
parser.add_argument('--pre-trained-model', default='./JSI-GAN_x4_exp1-native/JSI-GAN-1278420',
                    help='path to tensorflow pretrained model')
parser.add_argument('--save-path', default='./jsigan_x4.h5', help='Path to save h5 file')
args = parser.parse_args()


def tf_to_nn_param_map():
    """
    Map from tensorflow default param names to NNabla default param names
    """
    return {
        '/w': '/conv/W',
        '/b': '/conv/b',
    }


def rename_params(param_name):
    """
    Rename the tensorflow param names to corresponding NNabla param names
    """
    tf_to_nn_dict = tf_to_nn_param_map()
    for key in tf_to_nn_dict:
        if key in param_name:
            param_name = param_name.replace(key, tf_to_nn_dict[key])

    return param_name


def convert_tf_ckpt_to_nn_h5(ckpt_file, h5_file):
    """
    Convert the input checkpoint file to output hdf5 file
    """
    # Get tensorflow checkpoint reader
    reader = pywrap_tensorflow.NewCheckpointReader(ckpt_file)
    var_to_shape_map = reader.get_variable_to_shape_map()

    # Loop through each tensor name from the variable to shape map
    for key in sorted(var_to_shape_map):
        # Read tensor values for each tensor name
        name = key.split('/')
        if name[0].startswith('Network') and not name[-1].startswith('Adam'):
            weight = reader.get_tensor(key)
            if weight.ndim == 4:
                # transpose TF weight to NNabla weight format
                weight = np.transpose(weight, (3, 0, 1, 2))
            key = rename_params(key)

            # Create parameter with the same tensor name and shape
            params = get_parameter_or_create(key, shape=weight.shape)
            params.d = weight

    # Save to a h5 file
    nn.parameter.save_parameters(h5_file)


def main():
    """
    Conversion of file format from Tensorflow to NNabla
    """
    convert_tf_ckpt_to_nn_h5(args.pre_trained_model, args.save_path)
    params = nn.get_parameters()
    for key, value in params.items():
        print(key, value.shape)

    print('\nWeight conversion complete.')


if __name__ == '__main__':
    main()
