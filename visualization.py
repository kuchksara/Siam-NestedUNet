'''
This file is used to save the output image
'''

import torch.utils.data
from utils.parser import get_parser_with_args
from utils.helpers import get_test_loaders, initialize_metrics
import os
from tqdm import tqdm
import cv2
import numpy as np
import time

if not os.path.exists('./output_img_test'):
    os.mkdir('./output_img_test')

parser, metadata = get_parser_with_args()
opt = parser.parse_args()

dev = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

test_loader = get_test_loaders(opt, batch_size=1)

path = 'weights/snunet-32.pt'   # the path of the model
if dev == torch.device('cpu'):
    print('dev is {}'.format(dev))
    model = torch.load(path, map_location=torch.device('cpu'))
else:
    print('dev is {}'.format(dev))
    model = torch.load(path)


model.eval()
index_img = 0
test_metrics = initialize_metrics()
with torch.no_grad():
    tbar = tqdm(test_loader)
    for batch_img1, batch_img2, labels in tbar:
        t1 = time.time()
        batch_img1 = batch_img1.float().to(dev)
        batch_img2 = batch_img2.float().to(dev)
        labels = labels.long().to(dev)
        print(batch_img1.shape)
        cd_preds = model(batch_img1, batch_img2)

        cd_preds = cd_preds[-1]
#         print(type(cd_preds))
        _, cd_preds = torch.max(cd_preds, 1)
        cd_preds = cd_preds.data.cpu().numpy()
        t2 = time.time()
        print('change detection time is: {}'.format(t2 - t1))
        np.save('./output_img_test/change{}.npy'.format(index_img), cd_preds)
        cd_preds = cd_preds.squeeze() * 255

        file_path = './output_img_test/' + str(index_img).zfill(5)
        cv2.imwrite(file_path + '.png', cd_preds)

        index_img += 1
