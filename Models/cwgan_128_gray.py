import torch
import torch.nn as nn


class cWGAN_Generator_Gray_128(nn.Module):
    def __init__(self, z_dim, channels_img, features_g, num_classes, img_size, embed_size, dropout_prob=0.5) -> None:
        super(cWGAN_Generator_Gray_128, self).__init__()
        self.img_size = img_size
        self.dropout_prob = dropout_prob
        self.generator = nn.Sequential(
            # Input: N x z_dim x 1x1
            self._block(z_dim + embed_size, features_g*16,
                        4, 1, 0),  # N x features_g*16 x 16
            self._block(features_g*16, features_g*8, 4,
                        2, 1),  # N x features_g*8 x 8x8
            self._block(features_g*8, features_g*4, 4, 2,
                        1),  # N x features_g*4 x 16x16
            self._block(features_g*4, features_g*2, 4, 2,
                        1),  # N x features_g*2 x 32x32
            self._block(features_g*2, features_g, 4, 2,
                        1),  # N x  features_g x 64x64
            # N x channels_img x 128x128
            nn.ConvTranspose2d(features_g, channels_img,
                               kernel_size=4, stride=2, padding=1),
            nn.Tanh(),  # [-1, 1]
        )
        self.embedding = nn.Embedding(num_classes, embed_size)

    def _block(self, in_channels, out_channels, kernel_size, stride, padding):
        return nn.Sequential(
            nn.ConvTranspose2d(in_channels, out_channels,
                               kernel_size, stride, padding),  # deconvolution
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
        )

    def forward(self, x, labels):
        embedding = self.embedding(labels).unsqueeze(2).unsqueeze(3)
        x = torch.cat([x, embedding], dim=1)

        return self.generator(x)
