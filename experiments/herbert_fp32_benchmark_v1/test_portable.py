import unittest
from portable import PortableTokenizer

class PortableContractTest(unittest.TestCase):
    def tokenizer(self):
        return PortableTokenizer(dict(vocabulary=['<unk>','a','b','c</w>','ab','abc</w>','a</w>','!</w>','<mask>'],
            merges=[[1,2,4],[4,3,5]],unicodeRanges=[[0,0,1],[32,32,2],[33,33,8],[0x200b,0x200b,1]],
            addedTokens=[dict(content='<mask>',id=8)],specialTokenIds=dict(unk=0)))

    def test_suffix_and_ranked_merges(self):
        self.assertEqual(self.tokenizer().encode('abc'),[5])

    def test_punctuation_whitespace_and_dropped_control(self):
        self.assertEqual(self.tokenizer().encode('a ! a\x00'),[6,7,6])

    def test_special_is_found_before_cleaning(self):
        self.assertEqual(self.tokenizer().encode('a<mask>a'),[6,8,6])
        self.assertNotIn(8,self.tokenizer().encode('<ma\u200bsk>'))

    def test_unknowns_not_fused(self):
        self.assertEqual(self.tokenizer().encode('xx'),[0,0])

    def test_unpaired_surrogate_refused(self):
        with self.assertRaises(ValueError):self.tokenizer().encode('\ud800')

if __name__ == '__main__':unittest.main()
