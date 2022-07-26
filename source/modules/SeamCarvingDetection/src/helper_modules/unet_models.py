import tensorflow as tf
keras = tf.keras
from upsample import upsample
import sys

def get_model_by_name(model_name, model_params = None):

    if model_name == 'mobilenetv2':
        model = get_mobilenetv2_model(**model_params)
    elif model_name == 'resnet50v2':
        model = get_resnet50v2_model(**model_params)
    elif model_name == 'resnet50':
        model = get_resnet50_model(**model_params)
    elif model_name == 'resnet101v2':
        model = get_resnet101v2_model(**model_params)
    elif model_name == 'efficientnetb7':
        model = get_efficientnetb7_model(**model_params)
    else:
        print(f'Model name {model_name} not recognized.')
        sys.exit()
        
    return model


def get_efficientnetb7_model(input_augmentations = None, train_down_stack = True, output_channels = 1 , pretrained = False):
    weights = 'imagenet' if pretrained else None
    base_model = tf.keras.applications.EfficientNetB7(input_shape=[None, None, 3], include_top=False, weights = weights)
    layer_names = [
        'block2a_expand_activation',        # N/2 x N/2 x 64
        'block3a_expand_activation',  # N/4 x N/4 x 256
        'block4a_expand_activation',  # N/8 x N/8 x 512
        'block6a_expand_activation',  # N/16 x N/16 x 1024
        'top_activation',      # 4x4
    ]

    up_stack = [
        upsample(512, 3),  # 4x4 -> 8x8
        upsample(256, 3),  # 8x8 -> 16x16
        upsample(128, 3),  # 16x16 -> 32x32
        upsample(64, 3),   # 32x32 -> 64x64
    ]
    params = {
        'input_augmentations': input_augmentations,
        'train_down_stack': True,
        'output_channels': 1
    }
    return get_u_net_model(base_model, layer_names, up_stack, **params)


def get_resnet101v2_model(input_augmentations = None, train_down_stack = True, output_channels = 1 , pretrained = False):
    weights = 'imagenet' if pretrained else None
    base_model = tf.keras.applications.ResNet101V2(input_shape=[None, None, 3], include_top=False, weights = weights)
    layer_names = [
        'conv1_conv',        # N/2 x N/2 x 64
        'conv2_block3_1_relu',  # N/4 x N/4 x 256
        'conv3_block4_1_relu',  # N/8 x N/8 x 512
        'conv4_block23_1_relu',  # N/16 x N/16 x 1024
        'post_relu',      # 4x4
    ]

    up_stack = [
        upsample(512, 3),  # 4x4 -> 8x8
        upsample(256, 3),  # 8x8 -> 16x16
        upsample(128, 3),  # 16x16 -> 32x32
        upsample(64, 3),   # 32x32 -> 64x64
    ]
    params = {
        'input_augmentations': input_augmentations,
        'train_down_stack': True,
        'output_channels': 1
    }
    return get_u_net_model(base_model, layer_names, up_stack, **params)


def get_mobilenetv2_model(input_augmentations = None, train_down_stack = True, output_channels = 1 , pretrained = False):
    weights = 'imagenet' if pretrained else None
    base_model = tf.keras.applications.MobileNetV2(input_shape=[None, None, 3], include_top=False, weights = weights)
    layer_names = [
        'block_1_expand_relu',   # 64x64
        'block_3_expand_relu',   # 32x32
        'block_6_expand_relu',   # 16x16
        'block_13_expand_relu',  # 8x8
        'block_16_project',      # 4x4
    ]

    up_stack = [
        upsample(512, 3),  # 4x4 -> 8x8
        upsample(256, 3),  # 8x8 -> 16x16
        upsample(128, 3),  # 16x16 -> 32x32
        upsample(64, 3),   # 32x32 -> 64x64
    ]
    params = {
        'input_augmentations': input_augmentations,
        'train_down_stack': True,
        'output_channels': 1
    }
    return get_u_net_model(base_model, layer_names, up_stack, **params)


def get_resnet50v2_model(input_augmentations = None, train_down_stack = True, output_channels = 1 , pretrained = False):
    weights = 'imagenet' if pretrained else None
    base_model = keras.applications.ResNet50V2(input_shape = [None,None,3], include_top = False, weights = weights)

    # resnet layers to connect to upsampling layers
    layer_names = [
        'conv1_conv',        # N/2 x N/2 x 64
        'conv2_block3_1_relu',  # N/4 x N/4 x 256
        'conv3_block4_1_relu',  # N/8 x N/8 x 512
        'conv4_block6_1_relu',  # N/16 x N/16 x 1024
        'post_relu',  # N/32 x N/32 x 2048
    ]

    up_stack = [
            upsample(filters = 512, size = 3),  # N/32 x N/32 -> N/16 N/16
            upsample(filters = 256, size = 3),  # N/16 x N/16 -> N/8 N/8
            upsample(filters = 128, size = 3),  # N/8 x N/8 -> N/4 N/4
            upsample(filters = 64, size = 3),   # N/4 x N/4 -> N/2 N/2
        ]

    params = {
        'input_augmentations': input_augmentations,
        'train_down_stack': True,
        'output_channels': 1
    }

    return get_u_net_model(base_model, layer_names, up_stack, **params)

def get_resnet50_model(input_augmentations = None, train_down_stack = True, output_channels = 1, pretrained = False):
    weights = 'imagenet' if pretrained else None
    base_model = keras.applications.ResNet50(input_shape = [None,None,3], include_top = False, weights = weights)

    # resnet layers to connect to upsampling layers
    layer_names = [
        'conv1_relu',        # N/2 x N/2 x 64
        'conv2_block3_out',  # N/4 x N/4 x 256
        'conv3_block4_out',  # N/8 x N/8 x 512
        'conv4_block6_out',  # N/16 x N/16 x 1024
        'conv5_block3_out',  # N/32 x N/32 x 2048
    ]

    up_stack = [
            upsample(filters = 512, size = 3),  # N/32 x N/32 -> N/16 N/16
            upsample(filters = 256, size = 3),  # N/16 x N/16 -> N/8 N/8
            upsample(filters = 128, size = 3),  # N/8 x N/8 -> N/4 N/4
            upsample(filters = 64, size = 3),   # N/4 x N/4 -> N/2 N/2
        ]

    params = {
        'input_augmentations': input_augmentations,
        'train_down_stack': True,
        'output_channels': 1
    }

    return get_u_net_model(base_model, layer_names, up_stack, **params)

def get_u_net_model(base_model, layer_names, up_stack, input_augmentations = None, train_down_stack = True, output_channels = 1):


    layers = [base_model.get_layer(name).output for name in layer_names]

    down_stack = keras.Model(inputs = base_model.input, outputs = layers)
    down_stack.trainable = train_down_stack

    inputs = tf.keras.layers.Input(shape=[None, None, 3])

    if input_augmentations:
        x = input_augmentations(inputs)

    x = inputs

    # Downsampling through the model
    skips = down_stack(x)
    x = skips[-1] # last layer of the down_stack
    skips = reversed(skips[:-1]) # 2nd to last, 3rd to last, ...

    # Upsampling and establishing the skip connections
    for up, skip in zip(up_stack, skips):
        x = up(x)
        concat = tf.keras.layers.Concatenate()
        x = concat([x, skip])

    # This is the last layer of the model
    last = tf.keras.layers.Conv2DTranspose(
      output_channels, 3, strides=2,
      padding='same')   # N/2 x N/2 -> N x N

    x = last(x)

    return tf.keras.Model(inputs = inputs, outputs = x)
