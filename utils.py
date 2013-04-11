# -*- coding: utf-8 -*-

def transform(op1, op2):
    func = {0:del_del, 1:del_ins, 2:ins_del, 3:ins_ins}
    op2[1:] = func[op1[0]*2+op2[0]](op1[1:], op2[1:])
    return op2

def del_del(op1, op2):
    if op1[0] >= op2[0]+op2[1]:
        return op2
    if op1[0]+op1[1] <= op2[0]:
        op2[0] -= op1[1]
        return op2
    if op1[0] <= op2[0]:
        op2[1] = op2[0]+op2[1]-op1[0]-op1[1]
        if op2[1]<0:
            op2[1] = 0
        op2[0] = op1[0]+op1[1]
        return op2
    if op2[0]+op2[1] >= op1[0]+op1[1]:
        op2[1] -= op1[1]
        return op2
    op2[1] = op1[0]-op2[0]
    return op2

def del_ins(op1, op2):
    if op1[0] >= op2[0]:
        return op2
    if op1[0]+op1[1] <= op2[0]:
        op2[0] -= op1[1]
        return op2
    op2[0] = op1[0]
    return op2

def ins_del(op1, op2):
    if op1[0] <= op2[0]:
        op2[0] += len(op1[1])
        return op2
    if op2[0] > op1[0]+len(op1[1]):
        return op2
    op2[1] += len(op1[1])
    return op2

def ins_ins(op1, op2):
    if op1[0] >= op2[0]:
        return op2
    op2[0] += len(op1[1])
    return op2

def text_patch(text, patchs):
    for patch in patchs:
        if patch[0] == 1:
            text = text[0:patch[1]]+patch[2]+text[patch[1]:]
        if patch[0] == 0:
            text = text[0:patch[1]]+text[(patch[1]+patch[2]):]
    return text

def forward(pre_patches, patch):
    for pre in pre_patches:
        for i in xrange(len(patch)):
            patch[i] = transform(pre, patch[i])
    for i in xrange(len(patch)):
        for j in xrange(i+1, len(patch)):
            patch[j] = transform(patch[i], patch[j])
    return patch

######## unittest ################

import unittest

class TestUtils(unittest.TestCase):

    def test(self):
        origin = 'hello world'
        p = forward([], [[1, 0, 'aa'], [0, 6, 1]])
        text = text_patch(origin, p)
        self.assertEqual(text, 'aahello orld')
        p2 = forward([], [[1, 1, 'bb'], [0, 6, 1]])
        text = text_patch(text, p2)
        self.assertEqual(text, 'abbahell orld')
        p2 = forward(p, [[1, 1, 'bb'], [0, 6, 1]])
        text = text_patch(origin, p+p2)
        self.assertEqual(text, 'aahbbello orld')

if __name__ == '__main__':
    unittest.main()
