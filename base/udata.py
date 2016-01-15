"""
Copyright 2015-2016 Troy Hirni
This file is part of the pyrox project, distributed under
the terms of the GNU Affero General Public License.

UData - Unicode Data

Access to more information from the unicode character database.
"""


import struct, bisect

try:
	from ..base import *
except:
	from base import *


#
# BRACKETS
#

def bracket(c):
	"""
	Return a tuple with 'o' (open) or 'c' (close) indicator and the 
	matching bracket if given character is a bracket, else None.
	"""
	i = ord(c)
	x = bisect.bisect_left(BRACKETPAIRS, [i])
	BP = BRACKETPAIRS[x]
	return (BP[2], unichr(BP[1])) if (BP and BP[0]==i) else None




#
# BLOCKS
#

def block(c):
	"""
	Return block-name for the block containing the given character.
	"""
	i = ord(c)
	x = bisect.bisect_left(BLOCKS, [[i]])
	B = BLOCKS[x-1 if i>0 else 0]
	return B[1]




#
# PROPERTIES
#

def proplist(*a, **k):
	return PropList(*a, **k)




# UTILITY
def safechr(i):
	"""
	A workaround to prevent ValueError on narrow builds when creating
	characters with a codepoint over 0x10000.
	"""
	try:
		return unichr(i)
	except ValueError:
		return struct.pack('i', i).decode('utf-32') 





#
# DATA
#


# BidiBrackets
BRACKETPAIRS = [
	[0x0028, 0x0029, 'o'], [0x0029, 0x0028, 'c'],
	[0x005B, 0x005D, 'o'], [0x005D, 0x005B, 'c'],
	[0x007B, 0x007D, 'o'], [0x007D, 0x007B, 'c'],
	[0x0F3A, 0x0F3B, 'o'], [0x0F3B, 0x0F3A, 'c'],
	[0x0F3C, 0x0F3D, 'o'], [0x0F3D, 0x0F3C, 'c'],
	[0x169B, 0x169C, 'o'], [0x169C, 0x169B, 'c'],
	[0x2045, 0x2046, 'o'], [0x2046, 0x2045, 'c'],
	[0x207D, 0x207E, 'o'], [0x207E, 0x207D, 'c'],
	[0x208D, 0x208E, 'o'], [0x208E, 0x208D, 'c'],
	[0x2308, 0x2309, 'o'], [0x2309, 0x2308, 'c'],
	[0x230A, 0x230B, 'o'], [0x230B, 0x230A, 'c'],
	[0x2329, 0x232A, 'o'], [0x232A, 0x2329, 'c'],
	[0x2768, 0x2769, 'o'], [0x2769, 0x2768, 'c'],
	[0x276A, 0x276B, 'o'], [0x276B, 0x276A, 'c'],
	[0x276C, 0x276D, 'o'], [0x276D, 0x276C, 'c'],
	[0x276E, 0x276F, 'o'], [0x276F, 0x276E, 'c'],
	[0x2770, 0x2771, 'o'], [0x2771, 0x2770, 'c'],
	[0x2772, 0x2773, 'o'], [0x2773, 0x2772, 'c'],
	[0x2774, 0x2775, 'o'], [0x2775, 0x2774, 'c'],
	[0x27C5, 0x27C6, 'o'], [0x27C6, 0x27C5, 'c'],
	[0x27E6, 0x27E7, 'o'], [0x27E7, 0x27E6, 'c'],
	[0x27E8, 0x27E9, 'o'], [0x27E9, 0x27E8, 'c'],
	[0x27EA, 0x27EB, 'o'], [0x27EB, 0x27EA, 'c'],
	[0x27EC, 0x27ED, 'o'], [0x27ED, 0x27EC, 'c'],
	[0x27EE, 0x27EF, 'o'], [0x27EF, 0x27EE, 'c'],
	[0x2983, 0x2984, 'o'], [0x2984, 0x2983, 'c'],
	[0x2985, 0x2986, 'o'], [0x2986, 0x2985, 'c'],
	[0x2987, 0x2988, 'o'], [0x2988, 0x2987, 'c'],
	[0x2989, 0x298A, 'o'], [0x298A, 0x2989, 'c'],
	[0x298B, 0x298C, 'o'], [0x298C, 0x298B, 'c'],
	[0x298D, 0x2990, 'o'], [0x298E, 0x298F, 'c'],
	[0x298F, 0x298E, 'o'], [0x2990, 0x298D, 'c'],
	[0x2991, 0x2992, 'o'], [0x2992, 0x2991, 'c'],
	[0x2993, 0x2994, 'o'], [0x2994, 0x2993, 'c'],
	[0x2995, 0x2996, 'o'], [0x2996, 0x2995, 'c'],
	[0x2997, 0x2998, 'o'], [0x2998, 0x2997, 'c'],
	[0x29D8, 0x29D9, 'o'], [0x29D9, 0x29D8, 'c'],
	[0x29DA, 0x29DB, 'o'], [0x29DB, 0x29DA, 'c'],
	[0x29FC, 0x29FD, 'o'], [0x29FD, 0x29FC, 'c'],
	[0x2E22, 0x2E23, 'o'], [0x2E23, 0x2E22, 'c'],
	[0x2E24, 0x2E25, 'o'], [0x2E25, 0x2E24, 'c'],
	[0x2E26, 0x2E27, 'o'], [0x2E27, 0x2E26, 'c'],
	[0x2E28, 0x2E29, 'o'], [0x2E29, 0x2E28, 'c'],
	[0x3008, 0x3009, 'o'], [0x3009, 0x3008, 'c'],
	[0x300A, 0x300B, 'o'], [0x300B, 0x300A, 'c'],
	[0x300C, 0x300D, 'o'], [0x300D, 0x300C, 'c'],
	[0x300E, 0x300F, 'o'], [0x300F, 0x300E, 'c'],
	[0x3010, 0x3011, 'o'], [0x3011, 0x3010, 'c'],
	[0x3014, 0x3015, 'o'], [0x3015, 0x3014, 'c'],
	[0x3016, 0x3017, 'o'], [0x3017, 0x3016, 'c'],
	[0x3018, 0x3019, 'o'], [0x3019, 0x3018, 'c'],
	[0x301A, 0x301B, 'o'], [0x301B, 0x301A, 'c'],
	[0xFE59, 0xFE5A, 'o'], [0xFE5A, 0xFE59, 'c'],
	[0xFE5B, 0xFE5C, 'o'], [0xFE5C, 0xFE5B, 'c'],
	[0xFE5D, 0xFE5E, 'o'], [0xFE5E, 0xFE5D, 'c'],
	[0xFF08, 0xFF09, 'o'], [0xFF09, 0xFF08, 'c'],
	[0xFF3B, 0xFF3D, 'o'], [0xFF3D, 0xFF3B, 'c'],
	[0xFF5B, 0xFF5D, 'o'], [0xFF5D, 0xFF5B, 'c'],
	[0xFF5F, 0xFF60, 'o'], [0xFF60, 0xFF5F, 'c'],
	[0xFF62, 0xFF63, 'o'], [0xFF63, 0xFF62, 'c']
]



# Blocks
BLOCKS = [
	[[0x0000, 0x007F], 'Basic Latin'], [[0x0080, 0x00FF], 'Latin-1 Supplement'], [[0x0100, 0x017F], 'Latin Extended-A'], [[0x0180, 0x024F], 'Latin Extended-B'], 
	[[0x0250, 0x02AF], 'IPA Extensions'], [[0x02B0, 0x02FF], 'Spacing Modifier Letters'], [[0x0300, 0x036F], 'Combining Diacritical Marks'], 
	[[0x0370, 0x03FF], 'Greek and Coptic'], [[0x0400, 0x04FF], 'Cyrillic'], [[0x0500, 0x052F], 'Cyrillic Supplement'], [[0x0530, 0x058F], 'Armenian'], 
	[[0x0590, 0x05FF], 'Hebrew'], [[0x0600, 0x06FF], 'Arabic'], [[0x0700, 0x074F], 'Syriac'], [[0x0750, 0x077F], 'Arabic Supplement'], [[0x0780, 0x07BF], 'Thaana'], 
	[[0x07C0, 0x07FF], 'NKo'], [[0x0800, 0x083F], 'Samaritan'], [[0x0840, 0x085F], 'Mandaic'], [[0x08A0, 0x08FF], 'Arabic Extended-A'], 
	[[0x0900, 0x097F], 'Devanagari'], [[0x0980, 0x09FF], 'Bengali'], [[0x0A00, 0x0A7F], 'Gurmukhi'], [[0x0A80, 0x0AFF], 'Gujarati'], [[0x0B00, 0x0B7F], 'Oriya'], 
	[[0x0B80, 0x0BFF], 'Tamil'], [[0x0C00, 0x0C7F], 'Telugu'], [[0x0C80, 0x0CFF], 'Kannada'], [[0x0D00, 0x0D7F], 'Malayalam'], [[0x0D80, 0x0DFF], 'Sinhala'], 
	[[0x0E00, 0x0E7F], 'Thai'], [[0x0E80, 0x0EFF], 'Lao'], [[0x0F00, 0x0FFF], 'Tibetan'], [[0x1000, 0x109F], 'Myanmar'], [[0x10A0, 0x10FF], 'Georgian'], 
	[[0x1100, 0x11FF], 'Hangul Jamo'], [[0x1200, 0x137F], 'Ethiopic'], [[0x1380, 0x139F], 'Ethiopic Supplement'], [[0x13A0, 0x13FF], 'Cherokee'], 
	[[0x1400, 0x167F], 'Unified Canadian Aboriginal Syllabics'], [[0x1680, 0x169F], 'Ogham'], [[0x16A0, 0x16FF], 'Runic'], [[0x1700, 0x171F], 'Tagalog'], 
	[[0x1720, 0x173F], 'Hanunoo'], [[0x1740, 0x175F], 'Buhid'], [[0x1760, 0x177F], 'Tagbanwa'], [[0x1780, 0x17FF], 'Khmer'], [[0x1800, 0x18AF], 'Mongolian'], 
	[[0x18B0, 0x18FF], 'Unified Canadian Aboriginal Syllabics Extended'], [[0x1900, 0x194F], 'Limbu'], [[0x1950, 0x197F], 'Tai Le'], 
	[[0x1980, 0x19DF], 'New Tai Lue'], [[0x19E0, 0x19FF], 'Khmer Symbols'], [[0x1A00, 0x1A1F], 'Buginese'], [[0x1A20, 0x1AAF], 'Tai Tham'], 
	[[0x1AB0, 0x1AFF], 'Combining Diacritical Marks Extended'], [[0x1B00, 0x1B7F], 'Balinese'], [[0x1B80, 0x1BBF], 'Sundanese'], [[0x1BC0, 0x1BFF], 'Batak'], 
	[[0x1C00, 0x1C4F], 'Lepcha'], [[0x1C50, 0x1C7F], 'Ol Chiki'], [[0x1CC0, 0x1CCF], 'Sundanese Supplement'], [[0x1CD0, 0x1CFF], 'Vedic Extensions'], 
	[[0x1D00, 0x1D7F], 'Phonetic Extensions'], [[0x1D80, 0x1DBF], 'Phonetic Extensions Supplement'], [[0x1DC0, 0x1DFF], 'Combining Diacritical Marks Supplement'], 
	[[0x1E00, 0x1EFF], 'Latin Extended Additional'], [[0x1F00, 0x1FFF], 'Greek Extended'], [[0x2000, 0x206F], 'General Punctuation'], 
	[[0x2070, 0x209F], 'Superscripts and Subscripts'], [[0x20A0, 0x20CF], 'Currency Symbols'], [[0x20D0, 0x20FF], 'Combining Diacritical Marks for Symbols'], 
	[[0x2100, 0x214F], 'Letterlike Symbols'], [[0x2150, 0x218F], 'Number Forms'], [[0x2190, 0x21FF], 'Arrows'], [[0x2200, 0x22FF], 'Mathematical Operators'], 
	[[0x2300, 0x23FF], 'Miscellaneous Technical'], [[0x2400, 0x243F], 'Control Pictures'], [[0x2440, 0x245F], 'Optical Character Recognition'], 
	[[0x2460, 0x24FF], 'Enclosed Alphanumerics'], [[0x2500, 0x257F], 'Box Drawing'], [[0x2580, 0x259F], 'Block Elements'], [[0x25A0, 0x25FF], 'Geometric Shapes'], 
	[[0x2600, 0x26FF], 'Miscellaneous Symbols'], [[0x2700, 0x27BF], 'Dingbats'], [[0x27C0, 0x27EF], 'Miscellaneous Mathematical Symbols-A'], 
	[[0x27F0, 0x27FF], 'Supplemental Arrows-A'], [[0x2800, 0x28FF], 'Braille Patterns'], [[0x2900, 0x297F], 'Supplemental Arrows-B'], 
	[[0x2980, 0x29FF], 'Miscellaneous Mathematical Symbols-B'], [[0x2A00, 0x2AFF], 'Supplemental Mathematical Operators'], 
	[[0x2B00, 0x2BFF], 'Miscellaneous Symbols and Arrows'], [[0x2C00, 0x2C5F], 'Glagolitic'], [[0x2C60, 0x2C7F], 'Latin Extended-C'], [[0x2C80, 0x2CFF], 'Coptic'], 
	[[0x2D00, 0x2D2F], 'Georgian Supplement'], [[0x2D30, 0x2D7F], 'Tifinagh'], [[0x2D80, 0x2DDF], 'Ethiopic Extended'], [[0x2DE0, 0x2DFF], 'Cyrillic Extended-A'], 
	[[0x2E00, 0x2E7F], 'Supplemental Punctuation'], [[0x2E80, 0x2EFF], 'CJK Radicals Supplement'], [[0x2F00, 0x2FDF], 'Kangxi Radicals'], 
	[[0x2FF0, 0x2FFF], 'Ideographic Description Characters'], [[0x3000, 0x303F], 'CJK Symbols and Punctuation'], [[0x3040, 0x309F], 'Hiragana'], 
	[[0x30A0, 0x30FF], 'Katakana'], [[0x3100, 0x312F], 'Bopomofo'], [[0x3130, 0x318F], 'Hangul Compatibility Jamo'], [[0x3190, 0x319F], 'Kanbun'], 
	[[0x31A0, 0x31BF], 'Bopomofo Extended'], [[0x31C0, 0x31EF], 'CJK Strokes'], [[0x31F0, 0x31FF], 'Katakana Phonetic Extensions'], 
	[[0x3200, 0x32FF], 'Enclosed CJK Letters and Months'], [[0x3300, 0x33FF], 'CJK Compatibility'], [[0x3400, 0x4DBF], 'CJK Unified Ideographs Extension A'], 
	[[0x4DC0, 0x4DFF], 'Yijing Hexagram Symbols'], [[0x4E00, 0x9FFF], 'CJK Unified Ideographs'], [[0xA000, 0xA48F], 'Yi Syllables'], 
	[[0xA490, 0xA4CF], 'Yi Radicals'], [[0xA4D0, 0xA4FF], 'Lisu'], [[0xA500, 0xA63F], 'Vai'], [[0xA640, 0xA69F], 'Cyrillic Extended-B'], [[0xA6A0, 0xA6FF], 'Bamum'], 
	[[0xA700, 0xA71F], 'Modifier Tone Letters'], [[0xA720, 0xA7FF], 'Latin Extended-D'], [[0xA800, 0xA82F], 'Syloti Nagri'], 
	[[0xA830, 0xA83F], 'Common Indic Number Forms'], [[0xA840, 0xA87F], 'Phags-pa'], [[0xA880, 0xA8DF], 'Saurashtra'], [[0xA8E0, 0xA8FF], 'Devanagari Extended'], 
	[[0xA900, 0xA92F], 'Kayah Li'], [[0xA930, 0xA95F], 'Rejang'], [[0xA960, 0xA97F], 'Hangul Jamo Extended-A'], [[0xA980, 0xA9DF], 'Javanese'], 
	[[0xA9E0, 0xA9FF], 'Myanmar Extended-B'], [[0xAA00, 0xAA5F], 'Cham'], [[0xAA60, 0xAA7F], 'Myanmar Extended-A'], [[0xAA80, 0xAADF], 'Tai Viet'], 
	[[0xAAE0, 0xAAFF], 'Meetei Mayek Extensions'], [[0xAB00, 0xAB2F], 'Ethiopic Extended-A'], [[0xAB30, 0xAB6F], 'Latin Extended-E'], 
	[[0xAB70, 0xABBF], 'Cherokee Supplement'], [[0xABC0, 0xABFF], 'Meetei Mayek'], [[0xAC00, 0xD7AF], 'Hangul Syllables'], 
	[[0xD7B0, 0xD7FF], 'Hangul Jamo Extended-B'], [[0xD800, 0xDB7F], 'High Surrogates'], [[0xDB80, 0xDBFF], 'High Private Use Surrogates'], 
	[[0xDC00, 0xDFFF], 'Low Surrogates'], [[0xE000, 0xF8FF], 'Private Use Area'], [[0xF900, 0xFAFF], 'CJK Compatibility Ideographs'], 
	[[0xFB00, 0xFB4F], 'Alphabetic Presentation Forms'], [[0xFB50, 0xFDFF], 'Arabic Presentation Forms-A'], [[0xFE00, 0xFE0F], 'Variation Selectors'], 
	[[0xFE10, 0xFE1F], 'Vertical Forms'], [[0xFE20, 0xFE2F], 'Combining Half Marks'], [[0xFE30, 0xFE4F], 'CJK Compatibility Forms'], 
	[[0xFE50, 0xFE6F], 'Small Form Variants'], [[0xFE70, 0xFEFF], 'Arabic Presentation Forms-B'], [[0xFF00, 0xFFEF], 'Halfwidth and Fullwidth Forms'], 
	[[0xFFF0, 0xFFFF], 'Specials'], [[0x10000, 0x1007F], 'Linear B Syllabary'], [[0x10080, 0x100FF], 'Linear B Ideograms'], [[0x10100, 0x1013F], 'Aegean Numbers'], 
	[[0x10140, 0x1018F], 'Ancient Greek Numbers'], [[0x10190, 0x101CF], 'Ancient Symbols'], [[0x101D0, 0x101FF], 'Phaistos Disc'], [[0x10280, 0x1029F], 'Lycian'], 
	[[0x102A0, 0x102DF], 'Carian'], [[0x102E0, 0x102FF], 'Coptic Epact Numbers'], [[0x10300, 0x1032F], 'Old Italic'], [[0x10330, 0x1034F], 'Gothic'], 
	[[0x10350, 0x1037F], 'Old Permic'], [[0x10380, 0x1039F], 'Ugaritic'], [[0x103A0, 0x103DF], 'Old Persian'], [[0x10400, 0x1044F], 'Deseret'], 
	[[0x10450, 0x1047F], 'Shavian'], [[0x10480, 0x104AF], 'Osmanya'], [[0x10500, 0x1052F], 'Elbasan'], [[0x10530, 0x1056F], 'Caucasian Albanian'], 
	[[0x10600, 0x1077F], 'Linear A'], [[0x10800, 0x1083F], 'Cypriot Syllabary'], [[0x10840, 0x1085F], 'Imperial Aramaic'], [[0x10860, 0x1087F], 'Palmyrene'], 
	[[0x10880, 0x108AF], 'Nabataean'], [[0x108E0, 0x108FF], 'Hatran'], [[0x10900, 0x1091F], 'Phoenician'], [[0x10920, 0x1093F], 'Lydian'], 
	[[0x10980, 0x1099F], 'Meroitic Hieroglyphs'], [[0x109A0, 0x109FF], 'Meroitic Cursive'], [[0x10A00, 0x10A5F], 'Kharoshthi'], 
	[[0x10A60, 0x10A7F], 'Old South Arabian'], [[0x10A80, 0x10A9F], 'Old North Arabian'], [[0x10AC0, 0x10AFF], 'Manichaean'], [[0x10B00, 0x10B3F], 'Avestan'], 
	[[0x10B40, 0x10B5F], 'Inscriptional Parthian'], [[0x10B60, 0x10B7F], 'Inscriptional Pahlavi'], [[0x10B80, 0x10BAF], 'Psalter Pahlavi'], 
	[[0x10C00, 0x10C4F], 'Old Turkic'], [[0x10C80, 0x10CFF], 'Old Hungarian'], [[0x10E60, 0x10E7F], 'Rumi Numeral Symbols'], [[0x11000, 0x1107F], 'Brahmi'], 
	[[0x11080, 0x110CF], 'Kaithi'], [[0x110D0, 0x110FF], 'Sora Sompeng'], [[0x11100, 0x1114F], 'Chakma'], [[0x11150, 0x1117F], 'Mahajani'], 
	[[0x11180, 0x111DF], 'Sharada'], [[0x111E0, 0x111FF], 'Sinhala Archaic Numbers'], [[0x11200, 0x1124F], 'Khojki'], [[0x11280, 0x112AF], 'Multani'], 
	[[0x112B0, 0x112FF], 'Khudawadi'], [[0x11300, 0x1137F], 'Grantha'], [[0x11480, 0x114DF], 'Tirhuta'], [[0x11580, 0x115FF], 'Siddham'], 
	[[0x11600, 0x1165F], 'Modi'], [[0x11680, 0x116CF], 'Takri'], [[0x11700, 0x1173F], 'Ahom'], [[0x118A0, 0x118FF], 'Warang Citi'], 
	[[0x11AC0, 0x11AFF], 'Pau Cin Hau'], [[0x12000, 0x123FF], 'Cuneiform'], [[0x12400, 0x1247F], 'Cuneiform Numbers and Punctuation'], 
	[[0x12480, 0x1254F], 'Early Dynastic Cuneiform'], [[0x13000, 0x1342F], 'Egyptian Hieroglyphs'], [[0x14400, 0x1467F], 'Anatolian Hieroglyphs'], 
	[[0x16800, 0x16A3F], 'Bamum Supplement'], [[0x16A40, 0x16A6F], 'Mro'], [[0x16AD0, 0x16AFF], 'Bassa Vah'], [[0x16B00, 0x16B8F], 'Pahawh Hmong'], 
	[[0x16F00, 0x16F9F], 'Miao'], [[0x1B000, 0x1B0FF], 'Kana Supplement'], [[0x1BC00, 0x1BC9F], 'Duployan'], [[0x1BCA0, 0x1BCAF], 'Shorthand Format Controls'], 
	[[0x1D000, 0x1D0FF], 'Byzantine Musical Symbols'], [[0x1D100, 0x1D1FF], 'Musical Symbols'], [[0x1D200, 0x1D24F], 'Ancient Greek Musical Notation'], 
	[[0x1D300, 0x1D35F], 'Tai Xuan Jing Symbols'], [[0x1D360, 0x1D37F], 'Counting Rod Numerals'], [[0x1D400, 0x1D7FF], 'Mathematical Alphanumeric Symbols'], 
	[[0x1D800, 0x1DAAF], 'Sutton SignWriting'], [[0x1E800, 0x1E8DF], 'Mende Kikakui'], [[0x1EE00, 0x1EEFF], 'Arabic Mathematical Alphabetic Symbols'], 
	[[0x1F000, 0x1F02F], 'Mahjong Tiles'], [[0x1F030, 0x1F09F], 'Domino Tiles'], [[0x1F0A0, 0x1F0FF], 'Playing Cards'], 
	[[0x1F100, 0x1F1FF], 'Enclosed Alphanumeric Supplement'], [[0x1F200, 0x1F2FF], 'Enclosed Ideographic Supplement'], 
	[[0x1F300, 0x1F5FF], 'Miscellaneous Symbols and Pictographs'], [[0x1F600, 0x1F64F], 'Emoticons'], [[0x1F650, 0x1F67F], 'Ornamental Dingbats'], 
	[[0x1F680, 0x1F6FF], 'Transport and Map Symbols'], [[0x1F700, 0x1F77F], 'Alchemical Symbols'], [[0x1F780, 0x1F7FF], 'Geometric Shapes Extended'], 
	[[0x1F800, 0x1F8FF], 'Supplemental Arrows-C'], [[0x1F900, 0x1F9FF], 'Supplemental Symbols and Pictographs'], 
	[[0x20000, 0x2A6DF], 'CJK Unified Ideographs Extension B'], [[0x2A700, 0x2B73F], 'CJK Unified Ideographs Extension C'], 
	[[0x2B740, 0x2B81F], 'CJK Unified Ideographs Extension D'], [[0x2B820, 0x2CEAF], 'CJK Unified Ideographs Extension E'], 
	[[0x2F800, 0x2FA1F], 'CJK Compatibility Ideographs Supplement'], [[0xE0000, 0xE007F], 'Tags'], [[0xE0100, 0xE01EF], 'Variation Selectors Supplement'], 
	[[0xF0000, 0xFFFFF], 'Supplementary Private Use Area-A'], [[0x100000, 0x10FFFF], 'Supplementary Private Use Area-B']
]


class PropList(object):
	
	# PROP LIST CLASS VARIABLES
	__ITEMS = [
		[[0x0030,0x0039], [0x0041,0x0046], [0x0061,0x0066]],
		[0x061C, [0x200E,0x200F], [0x202A,0x202E], [0x2066,0x2069]],
		[0x002D, 0x058A, 0x05BE, 0x1400, 0x1806, [0x2010,0x2015], 0x2053, 0x207B, 0x208B, 0x2212, 0x2E17, 0x2E1A, [0x2E3A,0x2E3B], 0x2E40, 0x301C, 0x3030, 0x30A0, [0xFE31,0xFE32], 0xFE58, 0xFE63, 0xFF0D],
		[0x0149, 0x0673, 0x0F77, 0x0F79, [0x17A3,0x17A4], [0x206A,0x206F], 0x2329, 0x232A, 0xE0001, 0xE007F],
		[0x005E, 0x0060, 0x00A8, 0x00AF, 0x00B4, 0x00B7, 0x00B8, [0x02B0,0x02C1], [0x02C2,0x02C5], [0x02C6,0x02D1], [0x02D2,0x02DF], [0x02E0,0x02E4], [0x02E5,0x02EB], 0x02EC, 0x02ED, 0x02EE, [0x02EF,0x02FF], [0x0300,0x034E], [0x0350,0x0357], [0x035D,0x0362], 0x0374, 0x0375, 0x037A, [0x0384,0x0385], [0x0483,0x0487], 0x0559, [0x0591,0x05A1], [0x05A3,0x05BD], 0x05BF, [0x05C1,0x05C2], 0x05C4, [0x064B,0x0652], [0x0657,0x0658], [0x06DF,0x06E0], [0x06E5,0x06E6], [0x06EA,0x06EC], [0x0730,0x074A], [0x07A6,0x07B0], [0x07EB,0x07F3], [0x07F4,0x07F5], [0x0818,0x0819], [0x08E3,0x08FE], 0x093C, 0x094D, [0x0951,0x0954], 0x0971, 0x09BC, 0x09CD, 0x0A3C, 0x0A4D, 0x0ABC, 0x0ACD, 0x0B3C, 0x0B4D, 0x0BCD, 0x0C4D, 0x0CBC, 0x0CCD, 0x0D4D, 0x0DCA, [0x0E47,0x0E4C], 0x0E4E, [0x0EC8,0x0ECC], [0x0F18,0x0F19], 0x0F35, 0x0F37, 0x0F39, [0x0F3E,0x0F3F], [0x0F82,0x0F84], [0x0F86,0x0F87], 0x0FC6, 0x1037, [0x1039,0x103A], [0x1087,0x108C], 0x108D, 0x108F, [0x109A,0x109B], [0x17C9,0x17D3], 0x17DD, [0x1939,0x193B], [0x1A75,0x1A7C], 0x1A7F, [0x1AB0,0x1ABD], 0x1B34, 0x1B44, [0x1B6B,0x1B73], 0x1BAA, 0x1BAB, [0x1C36,0x1C37], [0x1C78,0x1C7D], [0x1CD0,0x1CD2], 0x1CD3, [0x1CD4,0x1CE0], 0x1CE1, [0x1CE2,0x1CE8], 0x1CED, 0x1CF4, [0x1CF8,0x1CF9], [0x1D2C,0x1D6A], [0x1DC4,0x1DCF], 0x1DF5, [0x1DFD,0x1DFF], 0x1FBD, [0x1FBF,0x1FC1], [0x1FCD,0x1FCF], [0x1FDD,0x1FDF], [0x1FED,0x1FEF], [0x1FFD,0x1FFE], [0x2CEF,0x2CF1], 0x2E2F, [0x302A,0x302D], [0x302E,0x302F], [0x3099,0x309A], [0x309B,0x309C], 0x30FC, 0xA66F, [0xA67C,0xA67D], 0xA67F, [0xA69C,0xA69D], [0xA6F0,0xA6F1], [0xA717,0xA71F], [0xA720,0xA721], 0xA788, [0xA7F8,0xA7F9], 0xA8C4, [0xA8E0,0xA8F1], [0xA92B,0xA92D], 0xA92E, 0xA953, 0xA9B3, 0xA9C0, 0xA9E5, 0xAA7B, 0xAA7C, 0xAA7D, 0xAABF, 0xAAC0, 0xAAC1, 0xAAC2, 0xAAF6, 0xAB5B, [0xAB5C,0xAB5F], 0xABEC, 0xABED, 0xFB1E, [0xFE20,0xFE2F], 0xFF3E, 0xFF40, 0xFF70, [0xFF9E,0xFF9F], 0xFFE3, 0x102E0, [0x10AE5,0x10AE6], [0x110B9,0x110BA], [0x11133,0x11134], 0x11173, 0x111C0, [0x111CA,0x111CC], 0x11235, 0x11236, [0x112E9,0x112EA], 0x1133C, 0x1134D, [0x11366,0x1136C], [0x11370,0x11374], [0x114C2,0x114C3], [0x115BF,0x115C0], 0x1163F, 0x116B6, 0x116B7, 0x1172B, [0x16AF0,0x16AF4], [0x16F8F,0x16F92], [0x16F93,0x16F9F], [0x1D167,0x1D169], [0x1D16D,0x1D172], [0x1D17B,0x1D182], [0x1D185,0x1D18B], [0x1D1AA,0x1D1AD], [0x1E8D0,0x1E8D6]],
		[0x00B7, [0x02D0,0x02D1], 0x0640, 0x07FA, 0x0E46, 0x0EC6, 0x180A, 0x1843, 0x1AA7, 0x1C36, 0x1C7B, 0x3005, [0x3031,0x3035], [0x309D,0x309E], [0x30FC,0x30FE], 0xA015, 0xA60C, 0xA9CF, 0xA9E6, 0xAA70, 0xAADD, [0xAAF3,0xAAF4], 0xFF70, 0x1135D, [0x115C6,0x115C8], [0x16B42,0x16B43]],
		[[0x0030,0x0039], [0x0041,0x0046], [0x0061,0x0066], [0xFF10,0xFF19], [0xFF21,0xFF26], [0xFF41,0xFF46]],
		[0x002D, 0x00AD, 0x058A, 0x1806, [0x2010,0x2011], 0x2E17, 0x30FB, 0xFE63, 0xFF0D, 0xFF65],
		[[0x2FF0,0x2FF1], [0x2FF4,0x2FFB]],
		[[0x2FF2,0x2FF3]],
		[0x3006, 0x3007, [0x3021,0x3029], [0x3038,0x303A], [0x3400,0x4DB5], [0x4E00,0x9FD5], [0xF900,0xFA6D], [0xFA70,0xFAD9], [0x20000,0x2A6D6], [0x2A700,0x2B734], [0x2B740,0x2B81D], [0x2B820,0x2CEA1], [0x2F800,0x2FA1D]],
		[[0x200C,0x200D]],
		[[0x0E40,0x0E44], [0x0EC0,0x0EC4], [0x19B5,0x19B7], 0x19BA, [0xAAB5,0xAAB6], 0xAAB9, [0xAABB,0xAABC]],
		[[0xFDD0,0xFDEF], [0xFFFE,0xFFFF], [0x1FFFE,0x1FFFF], [0x2FFFE,0x2FFFF], [0x3FFFE,0x3FFFF], [0x4FFFE,0x4FFFF], [0x5FFFE,0x5FFFF], [0x6FFFE,0x6FFFF], [0x7FFFE,0x7FFFF], [0x8FFFE,0x8FFFF], [0x9FFFE,0x9FFFF], [0xAFFFE,0xAFFFF], [0xBFFFE,0xBFFFF], [0xCFFFE,0xCFFFF], [0xDFFFE,0xDFFFF], [0xEFFFE,0xEFFFF], [0xFFFFE,0xFFFFF], [0x10FFFE,0x10FFFF]],
		[0x0345, [0x05B0,0x05BD], 0x05BF, [0x05C1,0x05C2], [0x05C4,0x05C5], 0x05C7, [0x0610,0x061A], [0x064B,0x0657], [0x0659,0x065F], 0x0670, [0x06D6,0x06DC], [0x06E1,0x06E4], [0x06E7,0x06E8], 0x06ED, 0x0711, [0x0730,0x073F], [0x07A6,0x07B0], [0x0816,0x0817], [0x081B,0x0823], [0x0825,0x0827], [0x0829,0x082C], [0x08E3,0x08E9], [0x08F0,0x0902], 0x0903, 0x093A, 0x093B, [0x093E,0x0940], [0x0941,0x0948], [0x0949,0x094C], [0x094E,0x094F], [0x0955,0x0957], [0x0962,0x0963], 0x0981, [0x0982,0x0983], [0x09BE,0x09C0], [0x09C1,0x09C4], [0x09C7,0x09C8], [0x09CB,0x09CC], 0x09D7, [0x09E2,0x09E3], [0x0A01,0x0A02], 0x0A03, [0x0A3E,0x0A40], [0x0A41,0x0A42], [0x0A47,0x0A48], [0x0A4B,0x0A4C], 0x0A51, [0x0A70,0x0A71], 0x0A75, [0x0A81,0x0A82], 0x0A83, [0x0ABE,0x0AC0], [0x0AC1,0x0AC5], [0x0AC7,0x0AC8], 0x0AC9, [0x0ACB,0x0ACC], [0x0AE2,0x0AE3], 0x0B01, [0x0B02,0x0B03], 0x0B3E, 0x0B3F, 0x0B40, [0x0B41,0x0B44], [0x0B47,0x0B48], [0x0B4B,0x0B4C], 0x0B56, 0x0B57, [0x0B62,0x0B63], 0x0B82, [0x0BBE,0x0BBF], 0x0BC0, [0x0BC1,0x0BC2], [0x0BC6,0x0BC8], [0x0BCA,0x0BCC], 0x0BD7, 0x0C00, [0x0C01,0x0C03], [0x0C3E,0x0C40], [0x0C41,0x0C44], [0x0C46,0x0C48], [0x0C4A,0x0C4C], [0x0C55,0x0C56], [0x0C62,0x0C63], 0x0C81, [0x0C82,0x0C83], 0x0CBE, 0x0CBF, [0x0CC0,0x0CC4], 0x0CC6, [0x0CC7,0x0CC8], [0x0CCA,0x0CCB], 0x0CCC, [0x0CD5,0x0CD6], [0x0CE2,0x0CE3], 0x0D01, [0x0D02,0x0D03], [0x0D3E,0x0D40], [0x0D41,0x0D44], [0x0D46,0x0D48], [0x0D4A,0x0D4C], 0x0D57, [0x0D62,0x0D63], [0x0D82,0x0D83], [0x0DCF,0x0DD1], [0x0DD2,0x0DD4], 0x0DD6, [0x0DD8,0x0DDF], [0x0DF2,0x0DF3], 0x0E31, [0x0E34,0x0E3A], 0x0E4D, 0x0EB1, [0x0EB4,0x0EB9], [0x0EBB,0x0EBC], 0x0ECD, [0x0F71,0x0F7E], 0x0F7F, [0x0F80,0x0F81], [0x0F8D,0x0F97], [0x0F99,0x0FBC], [0x102B,0x102C], [0x102D,0x1030], 0x1031, [0x1032,0x1036], 0x1038, [0x103B,0x103C], [0x103D,0x103E], [0x1056,0x1057], [0x1058,0x1059], [0x105E,0x1060], 0x1062, [0x1067,0x1068], [0x1071,0x1074], 0x1082, [0x1083,0x1084], [0x1085,0x1086], 0x109C, 0x109D, 0x135F, [0x1712,0x1713], [0x1732,0x1733], [0x1752,0x1753], [0x1772,0x1773], 0x17B6, [0x17B7,0x17BD], [0x17BE,0x17C5], 0x17C6, [0x17C7,0x17C8], 0x18A9, [0x1920,0x1922], [0x1923,0x1926], [0x1927,0x1928], [0x1929,0x192B], [0x1930,0x1931], 0x1932, [0x1933,0x1938], [0x1A17,0x1A18], [0x1A19,0x1A1A], 0x1A1B, 0x1A55, 0x1A56, 0x1A57, [0x1A58,0x1A5E], 0x1A61, 0x1A62, [0x1A63,0x1A64], [0x1A65,0x1A6C], [0x1A6D,0x1A72], [0x1A73,0x1A74], [0x1B00,0x1B03], 0x1B04, 0x1B35, [0x1B36,0x1B3A], 0x1B3B, 0x1B3C, [0x1B3D,0x1B41], 0x1B42, 0x1B43, [0x1B80,0x1B81], 0x1B82, 0x1BA1, [0x1BA2,0x1BA5], [0x1BA6,0x1BA7], [0x1BA8,0x1BA9], [0x1BAC,0x1BAD], 0x1BE7, [0x1BE8,0x1BE9], [0x1BEA,0x1BEC], 0x1BED, 0x1BEE, [0x1BEF,0x1BF1], [0x1C24,0x1C2B], [0x1C2C,0x1C33], [0x1C34,0x1C35], [0x1CF2,0x1CF3], [0x1DE7,0x1DF4], [0x24B6,0x24E9], [0x2DE0,0x2DFF], [0xA674,0xA67B], [0xA69E,0xA69F], [0xA823,0xA824], [0xA825,0xA826], 0xA827, [0xA880,0xA881], [0xA8B4,0xA8C3], [0xA926,0xA92A], [0xA947,0xA951], 0xA952, [0xA980,0xA982], 0xA983, [0xA9B4,0xA9B5], [0xA9B6,0xA9B9], [0xA9BA,0xA9BB], 0xA9BC, [0xA9BD,0xA9BF], [0xAA29,0xAA2E], [0xAA2F,0xAA30], [0xAA31,0xAA32], [0xAA33,0xAA34], [0xAA35,0xAA36], 0xAA43, 0xAA4C, 0xAA4D, 0xAAB0, [0xAAB2,0xAAB4], [0xAAB7,0xAAB8], 0xAABE, 0xAAEB, [0xAAEC,0xAAED], [0xAAEE,0xAAEF], 0xAAF5, [0xABE3,0xABE4], 0xABE5, [0xABE6,0xABE7], 0xABE8, [0xABE9,0xABEA], 0xFB1E, [0x10376,0x1037A], [0x10A01,0x10A03], [0x10A05,0x10A06], [0x10A0C,0x10A0F], 0x11000, 0x11001, 0x11002, [0x11038,0x11045], 0x11082, [0x110B0,0x110B2], [0x110B3,0x110B6], [0x110B7,0x110B8], [0x11100,0x11102], [0x11127,0x1112B], 0x1112C, [0x1112D,0x11132], [0x11180,0x11181], 0x11182, [0x111B3,0x111B5], [0x111B6,0x111BE], 0x111BF, [0x1122C,0x1122E], [0x1122F,0x11231], [0x11232,0x11233], 0x11234, 0x11237, 0x112DF, [0x112E0,0x112E2], [0x112E3,0x112E8], [0x11300,0x11301], [0x11302,0x11303], [0x1133E,0x1133F], 0x11340, [0x11341,0x11344], [0x11347,0x11348], [0x1134B,0x1134C], 0x11357, [0x11362,0x11363], [0x114B0,0x114B2], [0x114B3,0x114B8], 0x114B9, 0x114BA, [0x114BB,0x114BE], [0x114BF,0x114C0], 0x114C1, [0x115AF,0x115B1], [0x115B2,0x115B5], [0x115B8,0x115BB], [0x115BC,0x115BD], 0x115BE, [0x115DC,0x115DD], [0x11630,0x11632], [0x11633,0x1163A], [0x1163B,0x1163C], 0x1163D, 0x1163E, 0x11640, 0x116AB, 0x116AC, 0x116AD, [0x116AE,0x116AF], [0x116B0,0x116B5], [0x1171D,0x1171F], [0x11720,0x11721], [0x11722,0x11725], 0x11726, [0x11727,0x1172A], [0x16B30,0x16B36], [0x16F51,0x16F7E], 0x1BC9E, [0x1F130,0x1F149], [0x1F150,0x1F169], [0x1F170,0x1F189]],
		[0x034F, [0x115F,0x1160], [0x17B4,0x17B5], 0x2065, 0x3164, 0xFFA0, [0xFFF0,0xFFF8], 0xE0000, [0xE0002,0xE001F], [0xE0080,0xE00FF], [0xE01F0,0xE0FFF]],
		[0x09BE, 0x09D7, 0x0B3E, 0x0B57, 0x0BBE, 0x0BD7, 0x0CC2, [0x0CD5,0x0CD6], 0x0D3E, 0x0D57, 0x0DCF, 0x0DDF, [0x200C,0x200D], [0x302E,0x302F], [0xFF9E,0xFF9F], 0x1133E, 0x11357, 0x114B0, 0x114BD, 0x115AF, 0x1D165, [0x1D16E,0x1D172]],
		[0x00B7, 0x0387, [0x1369,0x1371], 0x19DA],
		[0x2118, 0x212E, [0x309B,0x309C]],
		[0x00AA, 0x00BA, [0x02B0,0x02B8], [0x02C0,0x02C1], [0x02E0,0x02E4], 0x0345, 0x037A, [0x1D2C,0x1D6A], 0x1D78, [0x1D9B,0x1DBF], 0x2071, 0x207F, [0x2090,0x209C], [0x2170,0x217F], [0x24D0,0x24E9], [0x2C7C,0x2C7D], [0xA69C,0xA69D], 0xA770, [0xA7F8,0xA7F9], [0xAB5C,0xAB5F]],
		[0x005E, [0x03D0,0x03D2], 0x03D5, [0x03F0,0x03F1], [0x03F4,0x03F5], 0x2016, [0x2032,0x2034], 0x2040, [0x2061,0x2064], 0x207D, 0x207E, 0x208D, 0x208E, [0x20D0,0x20DC], 0x20E1, [0x20E5,0x20E6], [0x20EB,0x20EF], 0x2102, 0x2107, [0x210A,0x2113], 0x2115, [0x2119,0x211D], 0x2124, 0x2128, 0x2129, [0x212C,0x212D], [0x212F,0x2131], [0x2133,0x2134], [0x2135,0x2138], [0x213C,0x213F], [0x2145,0x2149], [0x2195,0x2199], [0x219C,0x219F], [0x21A1,0x21A2], [0x21A4,0x21A5], 0x21A7, [0x21A9,0x21AD], [0x21B0,0x21B1], [0x21B6,0x21B7], [0x21BC,0x21CD], [0x21D0,0x21D1], 0x21D3, [0x21D5,0x21DB], 0x21DD, [0x21E4,0x21E5], 0x2308, 0x2309, 0x230A, 0x230B, [0x23B4,0x23B5], 0x23B7, 0x23D0, 0x23E2, [0x25A0,0x25A1], [0x25AE,0x25B6], [0x25BC,0x25C0], [0x25C6,0x25C7], [0x25CA,0x25CB], [0x25CF,0x25D3], 0x25E2, 0x25E4, [0x25E7,0x25EC], [0x2605,0x2606], 0x2640, 0x2642, [0x2660,0x2663], [0x266D,0x266E], 0x27C5, 0x27C6, 0x27E6, 0x27E7, 0x27E8, 0x27E9, 0x27EA, 0x27EB, 0x27EC, 0x27ED, 0x27EE, 0x27EF, 0x2983, 0x2984, 0x2985, 0x2986, 0x2987, 0x2988, 0x2989, 0x298A, 0x298B, 0x298C, 0x298D, 0x298E, 0x298F, 0x2990, 0x2991, 0x2992, 0x2993, 0x2994, 0x2995, 0x2996, 0x2997, 0x2998, 0x29D8, 0x29D9, 0x29DA, 0x29DB, 0x29FC, 0x29FD, 0xFE61, 0xFE63, 0xFE68, 0xFF3C, 0xFF3E, [0x1D400,0x1D454], [0x1D456,0x1D49C], [0x1D49E,0x1D49F], 0x1D4A2, [0x1D4A5,0x1D4A6], [0x1D4A9,0x1D4AC], [0x1D4AE,0x1D4B9], 0x1D4BB, [0x1D4BD,0x1D4C3], [0x1D4C5,0x1D505], [0x1D507,0x1D50A], [0x1D50D,0x1D514], [0x1D516,0x1D51C], [0x1D51E,0x1D539], [0x1D53B,0x1D53E], [0x1D540,0x1D544], 0x1D546, [0x1D54A,0x1D550], [0x1D552,0x1D6A5], [0x1D6A8,0x1D6C0], [0x1D6C2,0x1D6DA], [0x1D6DC,0x1D6FA], [0x1D6FC,0x1D714], [0x1D716,0x1D734], [0x1D736,0x1D74E], [0x1D750,0x1D76E], [0x1D770,0x1D788], [0x1D78A,0x1D7A8], [0x1D7AA,0x1D7C2], [0x1D7C4,0x1D7CB], [0x1D7CE,0x1D7FF], [0x1EE00,0x1EE03], [0x1EE05,0x1EE1F], [0x1EE21,0x1EE22], 0x1EE24, 0x1EE27, [0x1EE29,0x1EE32], [0x1EE34,0x1EE37], 0x1EE39, 0x1EE3B, 0x1EE42, 0x1EE47, 0x1EE49, 0x1EE4B, [0x1EE4D,0x1EE4F], [0x1EE51,0x1EE52], 0x1EE54, 0x1EE57, 0x1EE59, 0x1EE5B, 0x1EE5D, 0x1EE5F, [0x1EE61,0x1EE62], 0x1EE64, [0x1EE67,0x1EE6A], [0x1EE6C,0x1EE72], [0x1EE74,0x1EE77], [0x1EE79,0x1EE7C], 0x1EE7E, [0x1EE80,0x1EE89], [0x1EE8B,0x1EE9B], [0x1EEA1,0x1EEA3], [0x1EEA5,0x1EEA9], [0x1EEAB,0x1EEBB]],
		[[0x2160,0x216F], [0x24B6,0x24CF], [0x1F130,0x1F149], [0x1F150,0x1F169], [0x1F170,0x1F189]],
		[[0x0021,0x0023], 0x0024, [0x0025,0x0027], 0x0028, 0x0029, 0x002A, 0x002B, 0x002C, 0x002D, [0x002E,0x002F], [0x003A,0x003B], [0x003C,0x003E], [0x003F,0x0040], 0x005B, 0x005C, 0x005D, 0x005E, 0x0060, 0x007B, 0x007C, 0x007D, 0x007E, 0x00A1, [0x00A2,0x00A5], 0x00A6, 0x00A7, 0x00A9, 0x00AB, 0x00AC, 0x00AE, 0x00B0, 0x00B1, 0x00B6, 0x00BB, 0x00BF, 0x00D7, 0x00F7, [0x2010,0x2015], [0x2016,0x2017], 0x2018, 0x2019, 0x201A, [0x201B,0x201C], 0x201D, 0x201E, 0x201F, [0x2020,0x2027], [0x2030,0x2038], 0x2039, 0x203A, [0x203B,0x203E], [0x2041,0x2043], 0x2044, 0x2045, 0x2046, [0x2047,0x2051], 0x2052, 0x2053, [0x2055,0x205E], [0x2190,0x2194], [0x2195,0x2199], [0x219A,0x219B], [0x219C,0x219F], 0x21A0, [0x21A1,0x21A2], 0x21A3, [0x21A4,0x21A5], 0x21A6, [0x21A7,0x21AD], 0x21AE, [0x21AF,0x21CD], [0x21CE,0x21CF], [0x21D0,0x21D1], 0x21D2, 0x21D3, 0x21D4, [0x21D5,0x21F3], [0x21F4,0x22FF], [0x2300,0x2307], 0x2308, 0x2309, 0x230A, 0x230B, [0x230C,0x231F], [0x2320,0x2321], [0x2322,0x2328], 0x2329, 0x232A, [0x232B,0x237B], 0x237C, [0x237D,0x239A], [0x239B,0x23B3], [0x23B4,0x23DB], [0x23DC,0x23E1], [0x23E2,0x23FA], [0x23FB,0x23FF], [0x2400,0x2426], [0x2427,0x243F], [0x2440,0x244A], [0x244B,0x245F], [0x2500,0x25B6], 0x25B7, [0x25B8,0x25C0], 0x25C1, [0x25C2,0x25F7], [0x25F8,0x25FF], [0x2600,0x266E], 0x266F, [0x2670,0x2767], 0x2768, 0x2769, 0x276A, 0x276B, 0x276C, 0x276D, 0x276E, 0x276F, 0x2770, 0x2771, 0x2772, 0x2773, 0x2774, 0x2775, [0x2794,0x27BF], [0x27C0,0x27C4], 0x27C5, 0x27C6, [0x27C7,0x27E5], 0x27E6, 0x27E7, 0x27E8, 0x27E9, 0x27EA, 0x27EB, 0x27EC, 0x27ED, 0x27EE, 0x27EF, [0x27F0,0x27FF], [0x2800,0x28FF], [0x2900,0x2982], 0x2983, 0x2984, 0x2985, 0x2986, 0x2987, 0x2988, 0x2989, 0x298A, 0x298B, 0x298C, 0x298D, 0x298E, 0x298F, 0x2990, 0x2991, 0x2992, 0x2993, 0x2994, 0x2995, 0x2996, 0x2997, 0x2998, [0x2999,0x29D7], 0x29D8, 0x29D9, 0x29DA, 0x29DB, [0x29DC,0x29FB], 0x29FC, 0x29FD, [0x29FE,0x2AFF], [0x2B00,0x2B2F], [0x2B30,0x2B44], [0x2B45,0x2B46], [0x2B47,0x2B4C], [0x2B4D,0x2B73], [0x2B74,0x2B75], [0x2B76,0x2B95], [0x2B96,0x2B97], [0x2B98,0x2BB9], [0x2BBA,0x2BBC], [0x2BBD,0x2BC8], 0x2BC9, [0x2BCA,0x2BD1], [0x2BD2,0x2BEB], [0x2BEC,0x2BEF], [0x2BF0,0x2BFF], [0x2E00,0x2E01], 0x2E02, 0x2E03, 0x2E04, 0x2E05, [0x2E06,0x2E08], 0x2E09, 0x2E0A, 0x2E0B, 0x2E0C, 0x2E0D, [0x2E0E,0x2E16], 0x2E17, [0x2E18,0x2E19], 0x2E1A, 0x2E1B, 0x2E1C, 0x2E1D, [0x2E1E,0x2E1F], 0x2E20, 0x2E21, 0x2E22, 0x2E23, 0x2E24, 0x2E25, 0x2E26, 0x2E27, 0x2E28, 0x2E29, [0x2E2A,0x2E2E], 0x2E2F, [0x2E30,0x2E39], [0x2E3A,0x2E3B], [0x2E3C,0x2E3F], 0x2E40, 0x2E41, 0x2E42, [0x2E43,0x2E7F], [0x3001,0x3003], 0x3008, 0x3009, 0x300A, 0x300B, 0x300C, 0x300D, 0x300E, 0x300F, 0x3010, 0x3011, [0x3012,0x3013], 0x3014, 0x3015, 0x3016, 0x3017, 0x3018, 0x3019, 0x301A, 0x301B, 0x301C, 0x301D, [0x301E,0x301F], 0x3020, 0x3030, 0xFD3E, 0xFD3F, [0xFE45,0xFE46]],
		[[0x0009,0x000D], 0x0020, 0x0085, [0x200E,0x200F], 0x2028, 0x2029],
		[0x0022, 0x0027, 0x00AB, 0x00BB, 0x2018, 0x2019, 0x201A, [0x201B,0x201C], 0x201D, 0x201E, 0x201F, 0x2039, 0x203A, 0x2E42, 0x300C, 0x300D, 0x300E, 0x300F, 0x301D, [0x301E,0x301F], 0xFE41, 0xFE42, 0xFE43, 0xFE44, 0xFF02, 0xFF07, 0xFF62, 0xFF63],
		[[0x2E80,0x2E99], [0x2E9B,0x2EF3], [0x2F00,0x2FD5]],
		[0x0021, 0x002E, 0x003F, 0x0589, 0x061F, 0x06D4, [0x0700,0x0702], 0x07F9, [0x0964,0x0965], [0x104A,0x104B], 0x1362, [0x1367,0x1368], 0x166E, [0x1735,0x1736], 0x1803, 0x1809, [0x1944,0x1945], [0x1AA8,0x1AAB], [0x1B5A,0x1B5B], [0x1B5E,0x1B5F], [0x1C3B,0x1C3C], [0x1C7E,0x1C7F], [0x203C,0x203D], [0x2047,0x2049], 0x2E2E, 0x2E3C, 0x3002, 0xA4FF, [0xA60E,0xA60F], 0xA6F3, 0xA6F7, [0xA876,0xA877], [0xA8CE,0xA8CF], 0xA92F, [0xA9C8,0xA9C9], [0xAA5D,0xAA5F], [0xAAF0,0xAAF1], 0xABEB, 0xFE52, [0xFE56,0xFE57], 0xFF01, 0xFF0E, 0xFF1F, 0xFF61, [0x10A56,0x10A57], [0x11047,0x11048], [0x110BE,0x110C1], [0x11141,0x11143], [0x111C5,0x111C6], 0x111CD, [0x111DE,0x111DF], [0x11238,0x11239], [0x1123B,0x1123C], 0x112A9, [0x115C2,0x115C3], [0x115C9,0x115D7], [0x11641,0x11642], [0x1173C,0x1173E], [0x16A6E,0x16A6F], 0x16AF5, [0x16B37,0x16B38], 0x16B44, 0x1BC9F, 0x1DA88],
		[[0x0069,0x006A], 0x012F, 0x0249, 0x0268, 0x029D, 0x02B2, 0x03F3, 0x0456, 0x0458, 0x1D62, 0x1D96, 0x1DA4, 0x1DA8, 0x1E2D, 0x1ECB, 0x2071, [0x2148,0x2149], 0x2C7C, [0x1D422,0x1D423], [0x1D456,0x1D457], [0x1D48A,0x1D48B], [0x1D4BE,0x1D4BF], [0x1D4F2,0x1D4F3], [0x1D526,0x1D527], [0x1D55A,0x1D55B], [0x1D58E,0x1D58F], [0x1D5C2,0x1D5C3], [0x1D5F6,0x1D5F7], [0x1D62A,0x1D62B], [0x1D65E,0x1D65F], [0x1D692,0x1D693]],
		[0x0021, 0x002C, 0x002E, [0x003A,0x003B], 0x003F, 0x037E, 0x0387, 0x0589, 0x05C3, 0x060C, 0x061B, 0x061F, 0x06D4, [0x0700,0x070A], 0x070C, [0x07F8,0x07F9], [0x0830,0x083E], 0x085E, [0x0964,0x0965], [0x0E5A,0x0E5B], 0x0F08, [0x0F0D,0x0F12], [0x104A,0x104B], [0x1361,0x1368], [0x166D,0x166E], [0x16EB,0x16ED], [0x1735,0x1736], [0x17D4,0x17D6], 0x17DA, [0x1802,0x1805], [0x1808,0x1809], [0x1944,0x1945], [0x1AA8,0x1AAB], [0x1B5A,0x1B5B], [0x1B5D,0x1B5F], [0x1C3B,0x1C3F], [0x1C7E,0x1C7F], [0x203C,0x203D], [0x2047,0x2049], 0x2E2E, 0x2E3C, 0x2E41, [0x3001,0x3002], [0xA4FE,0xA4FF], [0xA60D,0xA60F], [0xA6F3,0xA6F7], [0xA876,0xA877], [0xA8CE,0xA8CF], 0xA92F, [0xA9C7,0xA9C9], [0xAA5D,0xAA5F], 0xAADF, [0xAAF0,0xAAF1], 0xABEB, [0xFE50,0xFE52], [0xFE54,0xFE57], 0xFF01, 0xFF0C, 0xFF0E, [0xFF1A,0xFF1B], 0xFF1F, 0xFF61, 0xFF64, 0x1039F, 0x103D0, 0x10857, 0x1091F, [0x10A56,0x10A57], [0x10AF0,0x10AF5], [0x10B3A,0x10B3F], [0x10B99,0x10B9C], [0x11047,0x1104D], [0x110BE,0x110C1], [0x11141,0x11143], [0x111C5,0x111C6], 0x111CD, [0x111DE,0x111DF], [0x11238,0x1123C], 0x112A9, [0x115C2,0x115C5], [0x115C9,0x115D7], [0x11641,0x11642], [0x1173C,0x1173E], [0x12470,0x12474], [0x16A6E,0x16A6F], 0x16AF5, [0x16B37,0x16B39], 0x16B44, 0x1BC9F, [0x1DA87,0x1DA8A]],
		[[0x3400,0x4DB5], [0x4E00,0x9FD5], [0xFA0E,0xFA0F], 0xFA11, [0xFA13,0xFA14], 0xFA1F, 0xFA21, [0xFA23,0xFA24], [0xFA27,0xFA29], [0x20000,0x2A6D6], [0x2A700,0x2B734], [0x2B740,0x2B81D], [0x2B820,0x2CEA1]],
		[[0x180B,0x180D], [0xFE00,0xFE0F], [0xE0100,0xE01EF]],
		[[0x0009,0x000D], 0x0020, 0x0085, 0x00A0, 0x1680, [0x2000,0x200A], 0x2028, 0x2029, 0x202F, 0x205F, 0x3000]
	]
	
	__KEYS = ['ASCII_Hex_Digit', 'Bidi_Control', 'Dash', 'Deprecated', 'Diacritic', 'Extender', 'Hex_Digit', 'Hyphen', 'IDS_Binary_Operator', 'IDS_Trinary_Operator', 'Ideographic', 'Join_Control', 'Logical_Order_Exception', 'Noncharacter_Code_Point', 'Other_Alphabetic', 'Other_Default_Ignorable_Code_Point', 'Other_Grapheme_Extend', 'Other_ID_Continue', 'Other_ID_Start', 'Other_Lowercase', 'Other_Math', 'Other_Uppercase', 'Pattern_Syntax', 'Pattern_White_Space', 'Quotation_Mark', 'Radical', 'STerm', 'Soft_Dotted', 'Terminal_Punctuation', 'Unified_Ideograph', 'Variation_Selector', 'White_Space']
	
	@classmethod
	def keylist(cls):
		"""Returns a copy of __KEYS."""
		return cls.__KEYS[:]
	
	@classmethod
	def indexof(cls, key):
		"""Find index of given key."""
		return bisect.bisect_left(cls.__KEYS, key)
	
	@classmethod
	def __item(cls, key):
		"""Private, to protect __ITEMS from manipulation."""
		return __ITEMS[bisect.bisect_left(cls.__KEYS, key)]
	
	def __init__(self, *a, **k):
		"""
		Pass a list of key strings, or keyword items, a list of integers.
		"""
		ii = k.get('items', [])
		for pname in a:
			if not pname in ii:
				ii.append(self.indexof(pname))
		
		self.__items = ii
		if not self.__items:
			raise ValueError('proplist-empty')
	
	@property
	def items(self):
		"""
		Return the list of items (integers) this object represents.
		"""
		return self.__items
	
	@property
	def keys(self):
		"""
		Return a list of item names (strings) this object represents.
		"""
		try:
			return self.__keys
		except:
			kk = []
			for i in self.__items:
				kk.append(self.__KEYS[i])
			self.__keys = kk
			return self.__keys
	
	def match(self, c):
		"""
		Return True if the given unichr matches one of the properties
		this object was created to represent.
		"""
		# loop through each proplist this object was created to represent
		x = ord(c)
		for listid in self.__items:
			proplist = self.__ITEMS[listid]
			for item in proplist:
				if isinstance(item, int):
					if x == item:
						return True
				else:
					if (x >= item[0]) and (x <= item[1]):
						return True
		return False
	
	def propgen(self):
		"""
		Return a generator for every character represented by this
		object.
		
		CAUTION: The list could be VERY long, so be careful trying to 
		         copy it.
		"""
		for listid in self.__items:
			proplist = self.__ITEMS[listid]
			for item in proplist:
				if isinstance(item, int):
					yield safechr(item)
				else:
					for x in range(*item):
						yield safechr(x)


